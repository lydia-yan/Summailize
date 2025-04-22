import { mergeStyles } from '@fluentui/react';

// Common styles for sections
export const sectionStyles = mergeStyles({
  padding: '16px',
  backgroundColor: '#fff',
  boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
  borderRadius: '4px',
  marginBottom: '16px'
});

// Common styles for headers
export const headerStyles = mergeStyles({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '4px'
});

// Common styles for subtitles
export const subtitleStyles = mergeStyles({
  fontSize: '14px',
  color: '#666666',
  marginBottom: '20px',
  fontFamily: 'Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Arial, sans-serif'
});

// Common text styles
export const textStyles = {
  title: mergeStyles({
    fontWeight: 600,
    marginBottom: '4px'
  }),
  category: mergeStyles({
    fontWeight: 'bold',
    display: 'block',
    marginBottom: '1px'
  }),
  content: mergeStyles({
    display: 'block',
    lineHeight: '1.5'
  })
}; 