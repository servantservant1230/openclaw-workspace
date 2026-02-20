export type Gender = 'male' | 'female';

export type NameType = {
  slug: string;
  label: string;
  desc: string;
  gender: Gender;
};

export const NAME_TYPES: NameType[] = [
  { slug: 'youngsoo', label: '영수', desc: '계획형·현실감각', gender: 'male' },
  { slug: 'youngho', label: '영호', desc: '부드러운 리더형', gender: 'male' },
  { slug: 'youngsik', label: '영식', desc: '센스·눈치 빠름', gender: 'male' },
  { slug: 'youngchul', label: '영철', desc: '직진·추진형', gender: 'male' },
  { slug: 'kwangsoo', label: '광수', desc: '개성·집중형', gender: 'male' },
  { slug: 'sangchul', label: '상철', desc: '안정·책임형', gender: 'male' },
  { slug: 'oksoon', label: '옥순', desc: '존재감·자신감형', gender: 'female' },
  { slug: 'youngsook', label: '영숙', desc: '배려·균형형', gender: 'female' },
  { slug: 'soonja', label: '순자', desc: '담백·차분형', gender: 'female' },
  { slug: 'youngja', label: '영자', desc: '솔직·쿨형', gender: 'female' },
  { slug: 'jungsook', label: '정숙', desc: '신중·정리형', gender: 'female' },
  { slug: 'hyunsook', label: '현숙', desc: '밝음·사교형', gender: 'female' }
];
