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
      if (!v) return;
      return new Promise(async (resolve) => {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        const urn = await Forma.proposal.getRootUrn();
        const [terrain] = await Forma.geometry.getPathsByCategory({ category: "terrain" })
        const builings = await Forma.geometry.getPathsByCategory({ category: "building" })

        const proposalBuildings = builings.filter((path) => path.split("/").length === 2)
        const surroundingBuildings = builings.filter((path) => path.split("/").length === 3)

        const basePath = surroundingBuildings[0].split("/").slice(0, 2).join("/")

        const triangles = [
          ...await Forma.geometry.getTriangles({ path: terrain }),
          ...await Forma.geometry.getTriangles({ path: basePath })
        ]

        const volumes = { "type": "FeatureCollection", features: [] };
        for (let path of proposalBuildings) {
          const geoApi = new EXPERIMENTAL_GeometryApi(Forma.getIframeMessenger());
          const featureCollection = await geoApi.EXPERIMENTAL_getVolume25DCollection({ urn, path })
          volumes.features.push(...featureCollection.features)
        }

        resolve(JSON.stringify({ volumes, triangles }));
      });
    },
    vizualize: function (result, data) {
      return new Promise(async (resolve) => {
        await new Promise((resolve) => setTimeout(resolve, 1000));
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
