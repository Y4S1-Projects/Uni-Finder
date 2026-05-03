import { twMerge } from "tailwind-merge";

export const careerFocusRing =
  "focus:outline-none focus:ring-2 focus:ring-indigo-500/30";

export const careerBaseButton = `px-5 py-2 rounded-xl font-medium transition-all duration-200 ease-in-out border border-transparent ${careerFocusRing} active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:active:scale-100`;

export const careerGradientButton =
  "bg-indigo-600 text-white hover:bg-indigo-700 shadow-md hover:shadow-lg hover:scale-[1.02] transition-all duration-200 ease-in-out";

export const careerNeutralButton =
  "bg-gray-100 hover:bg-gray-200 text-gray-700 border border-transparent";
export const careerMutedButton =
  "bg-gray-50 border border-gray-200 text-gray-700 hover:bg-indigo-50 hover:text-indigo-800 hover:border-indigo-200";


export const careerDangerOutlineButton =
  "bg-red-500 hover:bg-red-600 text-white border-transparent";

export const careerSecondaryDestructiveButton =
  "bg-white border border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700 hover:border-red-300";

export function mergeCareerButton(base, variant, className) {
  return twMerge(careerBaseButton, variant, className);
}
