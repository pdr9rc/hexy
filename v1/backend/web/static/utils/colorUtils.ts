/**
 * Color utilities for district and UI color generation.
 * Centralized color management for Mörk Borg aesthetic.
 */

/**
 * Generate a district color based on district name and available districts.
 * Uses authentic Mörk Borg color palette.
 * 
 * @param districtName - Name of the district
 * @param allDistricts - Array of all available districts (optional)
 * @returns Hex color string
 */
export function generateDistrictColor(districtName: string, allDistricts: string[] = []): string {
  // Authentic Mörk Borg color palette (12 colors for 12 districts max)
  const morkBorgColors = [
    '#FF00FF', // Magenta - Primary Mörk Borg color
    '#FFFF00', // Yellow - Primary Mörk Borg color
    '#00FFFF', // Cyan - Primary Mörk Borg color
    '#FF0000', // Red - Classic Mörk Borg accent
    '#00FF00', // Green - Classic Mörk Borg accent
    '#0000FF', // Blue - Classic Mörk Borg accent
    '#FF8000', // Orange - Mörk Borg warm tone
    '#8000FF', // Purple - Mörk Borg dark accent
    '#FF0080', // Hot Pink - Mörk Borg vibrant
    '#00FF80', // Spring Green - Mörk Borg bright
    '#FF4000', // Red-Orange - Mörk Borg fiery
    '#800080'  // Purple-Magenta - Mörk Borg deep
  ];
  
  // Use the old strategy: get district index from sorted array
  if (allDistricts.length > 0) {
    const sortedDistricts = [...allDistricts].sort();
    const districtIndex = sortedDistricts.indexOf(districtName);
    if (districtIndex >= 0) {
      return morkBorgColors[districtIndex % morkBorgColors.length];
    }
  }
  
  // Fallback: use hash of district name
  let hash = 0;
  for (let i = 0; i < districtName.length; i++) {
    const char = districtName.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  return morkBorgColors[Math.abs(hash) % morkBorgColors.length];
}

/**
 * Get a color from the Mörk Borg palette by index.
 * 
 * @param index - Index in the color palette
 * @returns Hex color string
 */
export function getMorkBorgColor(index: number): string {
  const morkBorgColors = [
    '#FF00FF', // Magenta
    '#FFFF00', // Yellow
    '#00FFFF', // Cyan
    '#FF0000', // Red
    '#00FF00', // Green
    '#0000FF', // Blue
    '#FF8000', // Orange
    '#8000FF', // Purple
    '#FF0080', // Hot Pink
    '#00FF80', // Spring Green
    '#FF4000', // Red-Orange
    '#800080'  // Purple-Magenta
  ];
  
  return morkBorgColors[index % morkBorgColors.length];
}

/**
 * Generate a consistent color for any string input.
 * Useful for generating colors for different content types.
 * 
 * @param input - String to generate color for
 * @returns Hex color string
 */
export function generateColorFromString(input: string): string {
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    const char = input.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  const morkBorgColors = [
    '#FF00FF', '#FFFF00', '#00FFFF', '#FF0000',
    '#00FF00', '#0000FF', '#FF8000', '#8000FF',
    '#FF0080', '#00FF80', '#FF4000', '#800080'
  ];
  
  return morkBorgColors[Math.abs(hash) % morkBorgColors.length];
} 