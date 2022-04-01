var pattern_list = [
  // solid fill
  { id: 'solid', transform: '', pattern: '' },

  {
    id: 'stripes-1r',
    transform: 'rotate(45)',
    pattern:
      '<line x1="0" y="0" x2="0" y2="50" stroke="#0d0d0d" stroke-width="10" />',
  },
  {
    id: 'stripes-2r',
    transform: 'rotate(45)',
    pattern:
      '<line x1="0" y="0" x2="0" y2="50" stroke="#0d0d0d" stroke-width="20" />',
  },
  {
    id: 'stripes-3r',
    transform: 'rotate(45)',
    pattern:
      '<line x1="0" y="0" x2="0" y2="50" stroke="#0d0d0d" stroke-width="30" />',
  },
  {
    id: 'stripes-4r',
    transform: 'rotate(45)',
    pattern:
      '<line x1="0" y="0" x2="0" y2="50" stroke="#0d0d0d" stroke-width="40" />',
  },

  {
    id: 'stripes-1l',
    transform: 'rotate(-45)',
    pattern:
      '<line x1="0" y="0" x2="0" y2="50" stroke="#0d0d0d" stroke-width="10" />',
  },
  {
    id: 'stripes-2l',
    transform: 'rotate(-45)',
    pattern:
      '<line x1="0" y="0" x2="0" y2="50" stroke="#0d0d0d" stroke-width="20" />',
  },
  {
    id: 'stripes-3l',
    transform: 'rotate(-45)',
    pattern:
      '<line x1="0" y="0" x2="0" y2="50" stroke="#0d0d0d" stroke-width="30" />',
  },
  {
    id: 'stripes-4l',
    transform: 'rotate(-45)',
    pattern:
      '<line x1="0" y="0" x2="0" y2="50" stroke="#0d0d0d" stroke-width="40" />',
  },

  {
    id: 'stripes-1v',
    transform: 'rotate(0)',
    pattern:
      '<line x1="0" y="0" x2="0" y2="50" stroke="#0d0d0d" stroke-width="10" />',
  },
  {
    id: 'stripes-2v',
    transform: 'rotate(0)',
    pattern:
      '<line x1="0" y="0" x2="0" y2="50" stroke="#0d0d0d" stroke-width="20" />',
  },
  {
    id: 'stripes-3v',
    transform: 'rotate(0)',
    pattern:
      '<line x1="0" y="0" x2="0" y2="50" stroke="#0d0d0d" stroke-width="30" />',
  },
  {
    id: 'stripes-4v',
    transform: 'rotate(0)',
    pattern:
      '<line x1="0" y="0" x2="0" y2="50" stroke="#0d0d0d" stroke-width="40" />',
  },
];

let i = 0;
pattern_list.forEach(p => {
  p['ind'] = i++;
});

export const patterns = pattern_list;
export const solid_fill = pattern_list[0];
