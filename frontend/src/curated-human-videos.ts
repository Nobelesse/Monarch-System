/**
 * Built-in, exercise-ID-specific instructor demonstrations.
 * These are embedded via the publishers' YouTube player, never downloaded,
 * copied, or represented as Monarch-owned footage.
 * Videos require an internet connection. Match is by EXACT catalog slug.
 * Curated here means an editor checked the publisher/title/description and
 * exercise relevance, NOT certified technique or medical clearance.
 */
export type InstructorDemo = {
  videoId: string;
  title: string;
  publisher: string;
  notes: string;
  start?: number;
};

export const instructorVideos: Readonly<Record<string, InstructorDemo>> = {
  'counter-pushup': {
    videoId: 'u883qxjOffE',
    title: 'Counter Push-Ups',
    publisher: 'KUTV 2 News Salt Lake City',
    notes: 'Counter-height incline push-up, with hands on a sturdy counter. This is the same movement as the exercise on your plan.',
  },
  'wall-pushup': {
    videoId: 'lIRpibTFB9I',
    title: 'Wall Push Up Exercise',
    publisher: 'Margaret Martin, Physical Therapist',
    notes: 'Wall variation only — not a substitute for countertop or floor push-ups.',
  },
  'floor-pushup': {
    videoId: 'pONDDchJjOI',
    title: 'Muscle Strengthening at Home — Push-ups',
    publisher: 'CDC',
    notes: 'Standard push-up demonstration. If this variation is too difficult, use your prescribed exercise instead.',
  },
  'bird-dog': {
    videoId: 'xEDnlOxeJH4',
    title: 'How to Do the Bird Dog Exercise',
    publisher: 'Hinge Health physical therapists',
    notes: 'A demonstration of the bird-dog exercise performed on hands and knees.',
  },
  'glute-bridge': {
    videoId: 'PhTDzR0TpZs',
    title: 'How to Do a Glute Bridge Exercise',
    publisher: 'Hinge Health physical therapists',
    notes: 'Glute bridge on the floor, pressing through the feet to raise the hips.',
  },
  'chair-sit-to-stand': {
    videoId: '1wAKXdS0Ark',
    title: 'Chair Standing Techniques',
    publisher: 'Front Row with Ed and Elizabeth',
    notes: 'Instructional sit-to-stand demonstration; follow the variation appropriate for your ability.',
  },
};

export function getInstructorDemo(slug: string): InstructorDemo | null {
  return Object.prototype.hasOwnProperty.call(instructorVideos, slug)
    ? instructorVideos[slug]
    : null;
}
