window.dash_clientside = Object.assign({}, window.dash_clientside, {
  forma: {
    getVolumes: function (v) {
      console.log(123);
      const geoApi = new EXPERIMENTAL_GeometryApi(Forma.getIframeMessenger());
      return new Promise(async (resolve) => {
        const urn = await Forma.proposal.getRootUrn();
        const paths = await Forma.selection.getSelection();

        const triangles = await Forma.geometry.getTriangles({
          path: "root",
          excludedPaths: [paths[0]],
        });

        if (paths.length) {
          const volumes = await geoApi.EXPERIMENTAL_getVolume25DCollection({
            urn,
            path: paths[0],
          });

          resolve(JSON.stringify({ volumes, triangles }));
        } else {
          resolve([]);
        }
      });
    },
  },
});
