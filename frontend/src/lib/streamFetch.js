/**
 * POST to url and parse the SSE response line-by-line, calling onEvent for
 * each parsed JSON data frame. Returns a promise that resolves when the
 * stream closes.
 *
 * SSE over POST is not supported by the native EventSource API, so we use
 * fetch + ReadableStream instead.
 */
export async function streamFetch(url, onEvent, onError) {
  let response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: { Accept: "text/event-stream" },
    });
  } catch (err) {
    onError?.(err.message || "Network error");
    return;
  }

  if (!response.ok) {
    onError?.(`Server error: ${response.status}`);
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE frames are separated by double-newlines; each line is "data: {...}"
    const frames = buffer.split("\n\n");
    // The last element may be a partial frame that arrived mid-chunk; retain it
    // and prepend it to the next read so no data is lost.
    buffer = frames.pop();

    for (const frame of frames) {
      for (const line of frame.split("\n")) {
        if (line.startsWith("data: ")) {
          try {
            const event = JSON.parse(line.slice(6));
            onEvent(event);
          } catch {
            // skip malformed frames
          }
        }
      }
    }
  }
}
