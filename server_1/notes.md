# Building My Own Web Server in Python

## Stage 1 — A Socket That Replies with Bytes (No HTTP Yet)

### Goal

Prove that:

- We can open a TCP socket
- A browser can connect to it
- Sending any bytes at all produces visible output

### Speaking Notes

- "A web server is just a program that listens on a TCP socket."
- "At this level, the browser is just a TCP client."
- "We haven't spoken HTTP yet — this is just bytes over a wire."
- Show that the browser displays something, even if it's an error or raw text.

---

## Stage 2 — Minimal Valid HTTP Response

### Goal

Introduce HTTP as a text protocol, not magic.

### Key Idea

Browsers expect:

- A status line
- Headers
- A blank line
- A body

### Speaking Notes

- "HTTP is just a convention layered on top of TCP."
- Walk through the response line by line.
- Emphasize `\r\n\r\n` as the boundary.
- This demystifies web frameworks immediately.

---

## Stage 3 — Read the Request and Print It

### Goal

Show that:

- The browser sends text
- We can inspect it
- Requests contain a lot more than we need

### Speaking Notes

- "The browser is chatty — we're ignoring 95% of this."
- Highlight the first line: `GET / HTTP/1.1`
- "Everything else is optional for us at this level."
- This motivates parsing only what we need.

---

## Stage 4 — Parse the Path and Serve One File

### Goal

Introduce:

- Request parsing
- Filesystem mapping
- The idea of "static files"

### New Concepts

- Path
- `GET /something`
- Returning different content
- Code (first real server feel)

### Speaking Notes

- "This is already recognisably a web server."
- "URLs become filesystem paths."
- "Frameworks mostly add safety, structure, and scale — not magic."
- Mention directory traversal risks without fixing them yet.

---

## Stage 5 — Response Construction and Content Types

### What This Version Is (Important)

- Still one responsibility per step, but not fully factored
- Introduces HTTP response construction as a concept
- Introduces content types, but inline
- Still has logic in `handle_client`
- Does not yet feel "framework-shaped"

This gives you a real pedagogical step, not just a refactor.

### What Changed from Stage 4

- We now name the idea of an HTTP response
- We separate protocol formatting from request handling
- We acknowledge that Content-Type exists, but don't abstract it yet

### What We Haven't Done Yet (Deliberately)

- No `resolve_request_path`
- No `get_content_type`
- No defaulting rules (`/about` → `about.html`)
- No reusable `http_response` helper
- No attempt at elegance

### Talking Points

- "This is the moment the server starts to look intentional."
- "We're still writing everything in one place, but we've identified the seams."
- "These seams are exactly where frameworks later insert abstractions."
- "Nothing new is possible yet — but the code is now ready to be improved."

---

## Stage 6 — Final Version (`blocking_server.py`)

### Why This Version Is Genuinely Different

You can now truthfully say:

> "The last jump is not about new behaviour — it's about isolating decisions."

### Three New Conceptual Things

1. **Normalises URLs** (`/`, extensionless paths)
2. **Encapsulates policy** (content type, defaults)
3. **Makes testing possible** (pure helper functions)

That makes the final jump structural, not cosmetic.

---

## Summary

Through these six stages, we've built a web server from first principles:

1. Raw TCP sockets
2. HTTP protocol basics
3. Request inspection
4. File serving
5. Response construction
6. Clean abstractions

Each stage introduces exactly one new concept, showing that web frameworks aren't magic — they're just organized solutions to familiar problems.