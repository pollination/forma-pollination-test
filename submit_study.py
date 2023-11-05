"""Submit Study to Pollination."""

import pathlib
import time
import requests
from requests.exceptions import HTTPError
import zipfile
import tempfile
import shutil

from typing import List

from pollination_streamlit.api.client import ApiClient
from pollination_streamlit.interactors import NewJob, Recipe, Job
from queenbee.job.job import JobStatusEnum


def submit_study(
    study_name: str, api_client: ApiClient, owner: str, project: str) -> Job:

    print(f'Creating a new study: {study_name}')
    # Assumption: the recipe has been already added to the project
    recipe = Recipe('ladybug-tools', 'daylight-factor', '0.8.13', client=api_client)

    # create a new study
    new_study = NewJob(owner, project, recipe, client=api_client)
    new_study.name = study_name
    new_study.description = f'Daylight factor study from Forma'

    model = pathlib.Path('model.hbjson')
    uploaded_path = new_study.upload_artifact(model, target_folder='forma')
    study_inputs = [
        {
            'model': uploaded_path,
            'radiance-parameters': '-ab 2 -aa 0.1 -ad 4096 -ar 256',
            'cpu-count': 120
        }
    ]

    # add the inputs to the study
    # each set of inputs create a new run
    new_study.arguments = study_inputs

    # # create the study
    running_study = new_study.create()

    job_url = f'https://app.pollination.cloud/{running_study.owner}/projects/{running_study.project}/jobs/{running_study.id}'
    print(job_url)
    time.sleep(5)
    return running_study


def check_study_status(study: Job):
    """"""
    status = study.status.status
    http_errors = 0
    while True:
        status_info = study.status
        print('\t# ------------------ #')
        print(f'\t# pending runs: {status_info.runs_pending}')
        print(f'\t# running runs: {status_info.runs_running}')
        print(f'\t# failed runs: {status_info.runs_failed}')
        print(f'\t# completed runs: {status_info.runs_completed}')
        if status in [
            JobStatusEnum.pre_processing, JobStatusEnum.running, JobStatusEnum.created,
            JobStatusEnum.unknown
        ]:
            time.sleep(15)
            try:
                study.refresh()
            except HTTPError as e:
                status_code = e.response.status_code
                print(str(e))
                if status_code == 500:
                    http_errors += 1
                    if http_errors > 3:
                        # failed for than 3 times with no success
                        raise HTTPError(e)
                    # wait for additional 15 seconds
                    time.sleep(10)
            else:
                http_errors = 0
                status = status_info.status
        else:
            # study is finished
            time.sleep(1)
            break


def _download_results(
    owner: str, project: str, study_id: int, download_folder: pathlib.Path,
    api_client: ApiClient
        ):
    print(f'Downloading page {1}')
    per_page = 25
    url = f'https://api.pollination.cloud/projects/{owner}/{project}/runs'
    params = {
        'job_id': study_id,
        'status': 'Succeeded',
        'page': 1,
        'per-page': per_page
    }
    response = requests.get(url, params=params, headers=api_client.headers)
    response_dict = response.json()
    run = response_dict['resources'][0]
    temp_folder = pathlib.Path('results')
    run_id = run['id']
    run_folder = temp_folder.joinpath('results')
    print(f'downloading results')
    run_folder.mkdir(parents=True, exist_ok=True)
    download_folder.mkdir(parents=True, exist_ok=True)
    url = f'https://api.pollination.cloud/projects/{owner}/{project}/runs/{run_id}/outputs/results'
    signed_url = requests.get(url, headers=api_client.headers)
    output = api_client.download_artifact(signed_url=signed_url.json())
    with zipfile.ZipFile(output) as zip_folder:
        zip_folder.extractall(run_folder.as_posix())


def download_study_results(
        api_client: ApiClient, study: Job, output_folder: pathlib.Path):
    owner = study.owner
    project = study.project
    study_id = study.id

    _download_results(
        owner=owner, project=project, study_id=study_id, download_folder=output_folder,
        api_client=api_client
    )


def run_study(are_you_serious=False):
    api_key = pathlib.Path('APIKEY').read_text().strip()
    assert api_key is not None, 'You must provide valid Pollination API key.'

    # project owner and project name - Change these!
    owner = 'ladybug-tools'
    project = 'demo'

    # change this to where the study folder is
    results_folder = pathlib.Path('results')
    name = 'Daylight fatcor study from Froma'
    api_client = ApiClient(api_token=api_key)
    if are_you_serious:
        study = submit_study(name, api_client, owner, project)
        # wait until the study is finished
        check_study_status(study=study)
        download_study_results(
            api_client=api_client, study=study, output_folder=results_folder
        )
    else:
        # read from a cached study
        _download_results(
            owner, project, study_id='08ea215e-312b-4018-a571-c3d10009cc99',
            download_folder=results_folder, api_client=api_client
        )