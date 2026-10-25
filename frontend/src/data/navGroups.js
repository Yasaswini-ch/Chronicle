export const NAV_GROUPS = [
  {
    key: 'people',
    label: 'People',
    items: [
      {
        label: 'Family Tree',
        route: 'explore/pantheon',
        hash: '#/explore/pantheon',
        desc: 'How the gods and heroes are related',
      },
      {
        label: 'Figures',
        route: 'explore/figures',
        hash: '#/explore/figures',
        desc: 'Profiles of gods, heroes and monsters',
      },
    ],
  },
  {
    key: 'world',
    label: 'World',
    items: [
      {
        label: 'Places',
        route: 'explore/gallery/places',
        hash: '#/explore/gallery/places',
        desc: 'Temples, cities and sites of the myths',
      },
      {
        label: 'Artifacts',
        route: 'explore/gallery/artifacts',
        hash: '#/explore/gallery/artifacts',
        desc: 'Sculptures, bronzes and tombs',
      },
    ],
  },
  {
    key: 'insights',
    label: 'Insights',
    items: [
      {
        label: 'Story Patterns',
        route: 'explore/motifs',
        hash: '#/explore/motifs',
        desc: 'Plots that repeat across myths',
      },
      {
        label: 'By The Numbers',
        route: 'explore/themes',
        hash: '#/explore/themes',
        desc: 'What shows up most',
      },
      {
        label: 'How It Was Built',
        route: 'explore/architecture',
        hash: '#/explore/architecture',
        desc: 'The language engine behind Chronicle',
      },
    ],
  },
];
