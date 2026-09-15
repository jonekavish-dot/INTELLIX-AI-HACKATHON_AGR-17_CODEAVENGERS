/**
 * Utility to parse operational notes into declarative shifts and actionable directives.
 *
 * Example:
 * Input: "Land Area changed from '2 hectares' to '5 hectares'. Action Required: Update portal validation filter to accept landholders up to 5 hectares."
 * Output: {
 *   shift: "Land Area changed from '2 hectares' to '5 hectares'.",
 *   action: "Update portal validation filter to accept landholders up to 5 hectares."
 * }
 */
export function parseOperationalNote(note) {
  if (!note || typeof note !== 'string') {
    return { shift: note || '', action: '' }
  }

  const trimmed = note.trim()
  const match = trimmed.match(/^(.*?)(?:\s*(?:Action Required:|Action:)\s*(.*))$/i)

  if (match && match[2]) {
    return {
      shift: match[1].trim(),
      action: match[2].trim(),
    }
  }

  return {
    shift: trimmed,
    action: '',
  }
}
