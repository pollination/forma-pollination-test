const scale = [
  [0, 0, 255, 255],
  [135, 206, 250, 255],
  [0, 255, 255, 255],
  [0, 128, 128, 255],
  [0, 255, 0, 255],
  [255, 255, 0, 255],
 [255, 165, 0, 255],
  [255, 0, 0, 255]
]

const max = 2;

window.dash_clientside = Object.assign({}, window.dash_clientside, {
  forma: {
    getVolumes: function (v) {
      return new Promise(async (resolve) => {
        const urn = await Forma.proposal.getRootUrn();
        const paths = await Forma.selection.getSelection();

        const triangles = [
          ...(await Forma.geometry.getTriangles({
            path: "root"
          })),
        ];

        if (paths.length) {
          const geoApi = new EXPERIMENTAL_GeometryApi(Forma.getIframeMessenger());
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
    vizualize: function (result, data) {
      return new Promise(async (resolve) => {
      const resolution = 0.5;
      const position = [];
      const colors = [];

      for (let sensor of data) {
        const {x, y, z, v} = sensor

        position.push(
          x - resolution,
          y - resolution,
          z,
          x + resolution,
          y - resolution,
          z,
          x - resolution,
          y + resolution,
          z,
          x - resolution,
          y + resolution,
          z,
          x + resolution,
          y - resolution,
          z,
          x + resolution,
          y + resolution,
          z
        );

        const idx = Math.min(Math.floor(v / max * scale.length), scale.length - 1);

        colors.push(...scale[idx], ...scale[idx], ...scale[idx],
          ...scale[idx],
          ...scale[idx],
          ...scale[idx]
        );
      }

      await Forma.render.addMesh({ geometryData: { 
        position: new Float32Array(position), 
        color: new Uint8Array(colors) 
      }})

      resolve();

    });


    }
  },
});
