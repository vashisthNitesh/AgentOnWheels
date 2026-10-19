/**
 * AgentOnWheels Tailwind Theme Preset
 * Exposes design tokens as Tailwind utility classes with opacity support.
 */

function withOpacity(variableName) {
  return ({ opacityValue }) => {
    if (opacityValue !== undefined) {
      return `rgb(var(${variableName}) / ${opacityValue})`
    }
    return `rgb(var(${variableName}))`
  }
}

export default {
  darkMode: 'class',
  theme: {
    extend: {
      textColor: {
        'primary': withOpacity('--text-primary'),
        'secondary': withOpacity('--text-secondary'),
        'muted': withOpacity('--text-muted'),
        'on-primary': withOpacity('--text-on-primary'),
      },
      placeholderColor: {
        'muted': withOpacity('--text-muted'),
        'secondary': withOpacity('--text-secondary'),
        'primary': withOpacity('--text-primary'),
      },
      backgroundColor: {
        'app': withOpacity('--bg-app'),
        'surface': withOpacity('--bg-surface'),
        'surface-raised': withOpacity('--bg-surface-raised'),
        'subtle': withOpacity('--bg-subtle'),
        'muted': withOpacity('--bg-muted'),
      },
      borderColor: {
        'default': withOpacity('--border-default'),
        'strong': withOpacity('--border-strong'),
        'border-default': withOpacity('--border-default'),
        'border-strong': withOpacity('--border-strong'),
      },
      colors: {
        // Semantic Surfaces & Aliases
        'app': withOpacity('--bg-app'),
        'surface': withOpacity('--bg-surface'),
        'surface-raised': withOpacity('--bg-surface-raised'),
        'subtle': withOpacity('--bg-subtle'),
        'muted': withOpacity('--text-muted'), // Ensures fallback for utilities is text-muted
        'bg-muted': withOpacity('--bg-muted'),

        // Semantic Borders
        'border-default': withOpacity('--border-default'),
        'border-strong': withOpacity('--border-strong'),

        // Semantic Text Aliases
        'text-primary': withOpacity('--text-primary'),
        'text-secondary': withOpacity('--text-secondary'),
        'text-muted': withOpacity('--text-muted'),
        'text-on-primary': withOpacity('--text-on-primary'),

        // Brand Primary Scale (Indigo)
        primary: {
          50: withOpacity('--color-primary-50'),
          100: withOpacity('--color-primary-100'),
          200: withOpacity('--color-primary-200'),
          300: withOpacity('--color-primary-300'),
          400: withOpacity('--color-primary-400'),
          500: withOpacity('--color-primary-500'),
          600: withOpacity('--color-primary-600'),
          700: withOpacity('--color-primary-700'),
          800: withOpacity('--color-primary-800'),
          900: withOpacity('--color-primary-900'),
          950: withOpacity('--color-primary-950'),
        },

        // Brand Accent Scale (Teal)
        accent: {
          50: withOpacity('--color-accent-50'),
          100: withOpacity('--color-accent-100'),
          200: withOpacity('--color-accent-200'),
          300: withOpacity('--color-accent-300'),
          400: withOpacity('--color-accent-400'),
          500: withOpacity('--color-accent-500'),
          600: withOpacity('--color-accent-600'),
          700: withOpacity('--color-accent-700'),
          800: withOpacity('--color-accent-800'),
          900: withOpacity('--color-accent-900'),
          950: withOpacity('--color-accent-950'),
        },

        // Semantic States
        success: {
          50: withOpacity('--color-success-50'),
          100: withOpacity('--color-success-100'),
          500: withOpacity('--color-success-500'),
          600: withOpacity('--color-success-600'),
          700: withOpacity('--color-success-700'),
        },
        warning: {
          50: withOpacity('--color-warning-50'),
          100: withOpacity('--color-warning-100'),
          500: withOpacity('--color-warning-500'),
          600: withOpacity('--color-warning-600'),
          700: withOpacity('--color-warning-700'),
        },
        danger: {
          50: withOpacity('--color-danger-50'),
          100: withOpacity('--color-danger-100'),
          500: withOpacity('--color-danger-500'),
          600: withOpacity('--color-danger-600'),
          700: withOpacity('--color-danger-700'),
        },
        info: {
          50: withOpacity('--color-info-50'),
          100: withOpacity('--color-info-100'),
          500: withOpacity('--color-info-500'),
          600: withOpacity('--color-info-600'),
          700: withOpacity('--color-info-700'),
        },
      },
      zIndex: {
        '0': '0',
        '10': '10',
        '20': '20',
        '30': '30',
        '40': '40',
        '50': '50',
        'dropdown': '1000',
        'sticky': '1020',
        'fixed': '1030',
        'drawer': '1040',
        'modal': '1050',
        'popover': '1060',
        'tooltip': '1070',
        'toast': '1080',
      },
      fontFamily: {
        sans: ['Inter Variable', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono Variable', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      boxShadow: {
        'xs': 'var(--shadow-xs)',
        'sm': 'var(--shadow-sm)',
        'md': 'var(--shadow-md)',
        'lg': 'var(--shadow-lg)',
        'xl': 'var(--shadow-xl)',
      },
      borderRadius: {
        'sm': '6px',
        'md': '10px',
        'lg': '12px',
        'xl': '14px',
      },
    },
  },
}
