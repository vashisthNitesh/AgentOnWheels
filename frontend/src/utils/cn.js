import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Combines conditional classes using clsx and intelligently merges Tailwind classes.
 * @param {...any} inputs
 * @returns {string}
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs))
}
