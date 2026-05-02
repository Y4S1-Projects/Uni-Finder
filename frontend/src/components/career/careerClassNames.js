import { twMerge } from "tailwind-merge";

export const careerBaseButton =
  "px-4 py-2 rounded-xl font-medium transition-all duration-200 border border-transparent focus:outline-none focus:ring-2 focus:ring-purple-500/40 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100";

export const careerGradientButton =
  "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md hover:shadow-lg hover:scale-[1.02]";

export const careerSecondaryButton =
  "bg-white/70 backdrop-blur border border-gray-200 text-gray-700 hover:bg-red-50 hover:text-red-600 hover:border-red-200/80";

export const careerMutedButton =
  "bg-white/70 backdrop-blur border border-gray-200 text-gray-700 hover:bg-purple-50 hover:text-purple-800 hover:border-purple-200/80";

export const careerDangerOutlineButton =
  "bg-white/70 backdrop-blur border border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300";

export function mergeCareerButton(base, variant, className) {
  return twMerge(careerBaseButton, variant, className);
}
