# AdonisJS 7.x — Coding Agent Reference Document

**Runtime requirements:** Node.js 24+, TypeScript 5.9/6.0, ESLint 10, Vite 7. Released Feb 25, 2026.

## 1. Project Structure

AdonisJS v7 follows a monolithic-friendly layout where every concern has a dedicated directory under `app/`. The `#`-prefixed subpath imports (defined in `package.json`) replace relative paths everywhere.

```text
my-app/
├── app/
│   ├── controllers/          # HTTP controllers (thin)
│   ├── services/             # Business logic
│   ├── validators/           # VineJS validator schemas
│   ├── middleware/           # Custom middleware
│   ├── models/               # Lucid ORM models
│   ├── transformers/         # Response serialization (NEW in v7)
│   ├── policies/             # Bouncer authorization
│   ├── exceptions/           # Custom exception classes
│   ├── helpers/              # Pure utility functions
│   └── jobs/                 # Queue jobs
├── config/                   # Framework config files
├── database/
│   ├── migrations/
│   ├── seeders/
│   └── schema/               # Auto-generated Lucid schema classes (v7)
├── resources/
│   └── views/                # Edge.js templates
├── start/
│   ├── routes.ts             # Route definitions
│   ├── kernel.ts             # Middleware stack
│   └── env.ts                # Env validation
├── .adonisjs/
│   └── server/               # Auto-generated barrel files (v7)
│       ├── controllers.ts
│       ├── events.ts
│       └── policies.ts
├── tests/
│   ├── unit/
│   └── functional/
├── adonisrc.ts
└── package.json
```

### `package.json` subpath imports (required in v7):

```json
{
  "imports": {
    "#controllers/*": "./app/controllers/*.js",
    "#services/*":    "./app/services/*.js",
    "#validators/*":  "./app/validators/*.js",
    "#middleware/*":  "./app/middleware/*.js",
    "#models/*":      "./app/models/*.js",
    "#transformers/*":"./app/transformers/*.js",
    "#helpers/*":     "./app/helpers/*.js",
    "#generated/*":   "./.adonisjs/server/*.js",
    "#database/*":    "./database/*.js",
    "#start/*":       "./start/*.js"
  }
}
```

### Naming Conventions

| Entity | File name | Class name |
| :--- | :--- | :--- |
| Controller | `posts_controller.ts` | `PostsController` |
| Service | `post_service.ts` | `PostService` |
| Validator | `post_validator.ts` | (exported const, not class) |
| Model | `post.ts` | `Post` |
| Transformer | `post_transformer.ts` | `PostTransformer` |
| Middleware | `auth_middleware.ts` | `AuthMiddleware` |
| Exception | `app_exception.ts` | `AppException` |

Routes use snake_case segments: `/blog-posts` → `:blogPostId`. Methods use camelCase. Named routes follow auto-generated controller.method convention (e.g., `posts.show`).

### v6 → v7 Structure Changes

*   Barrel files generated at `.adonisjs/server/controllers.ts` — no more wall of lazy imports in routes
*   `#generated/*` subpath import added for barrel files
*   `#transformers/*` and `#database/*` subpaths added
*   `inertia/app/app.tsx` → `inertia/app.tsx` (Inertia entry point moved)

### Fat Controller Anti-Pattern — What NOT to put in controllers

❌ **Never put in a controller:**

*   Raw SQL or ORM queries beyond simple `.findOrFail()`
*   Business rule enforcement (e.g., "a post can only be published if user is verified")
*   Sending emails, pushing jobs, or calling external APIs
*   File system I/O
*   Multi-step transaction logic

---

## 2. Controllers

Controllers must be thin orchestrators: validate input → call a service → serialize output.

### Thin Controller Pattern

```typescript
// app/controllers/posts_controller.ts
import type { HttpContext } from '@adonisjs/core/http'
import { inject } from '@adonisjs/core'
import { createPostValidator, updatePostValidator } from '#validators/post_validator'
import PostService from '#services/post_service'
import PostTransformer from '#transformers/post_transformer'

@inject()
export default class PostsController {
  constructor(private postService: PostService) {}

  async index({ request, serialize }: HttpContext) {
    const page = request.input('page', 1)
    const posts = await this.postService.paginate(page)
    return serialize({ posts: PostTransformer.transform(posts) })
  }

  async show({ params, serialize }: HttpContext) {
    const post = await this.postService.findOrFail(params.id)
    return serialize({ post: PostTransformer.transform(post) })
  }

  async store({ request, response, serialize }: HttpContext) {
    const payload = await request.validateUsing(createPostValidator)
    const post = await this.postService.create(payload)
    return response
      .status(201)
      .send(serialize({ post: PostTransformer.transform(post) }))
  }

  async update({ params, request, serialize }: HttpContext) {
    const payload = await request.validateUsing(updatePostValidator)
    const post = await this.postService.update(params.id, payload)
    return serialize({ post: PostTransformer.transform(post) })
  }

  async destroy({ params, response }: HttpContext) {
    await this.postService.delete(params.id)
    return response.noContent()
  }
}
```

**Key rules:**

*   Use `@inject()` + constructor injection — never `app.container.make()` inside methods
*   Call `request.validateUsing(validator)` — do not write inline `.only()` + manual checks
*   Use `serialize()` from `HttpContext` for JSON responses (v7 transformer pattern)
*   Use `response.noContent()` for 204, `response.status(201)` for creates

### `response.json()` vs `view.render()`

```typescript
// JSON API response — use serialize() with a transformer (v7 preferred)
return serialize({ post: PostTransformer.transform(post) })

// Legacy JSON (acceptable for simple responses without transformers)
return response.json({ message: 'ok' })

// Edge template (hypermedia/HTMX apps)
return view.render('posts/show', { post })

// HTMX partial (see Section 8)
if (request.header('HX-Request')) {
  return view.render('posts/_post_card', { post })
}
return view.render('posts/show', { post })
```

### Controller-Level Error Handling

Do not try/catch in controllers unless you need to transform specific errors. Let the global exception handler (Section 11) do the work.

```typescript
// ✅ Correct — no try/catch needed; exceptions propagate to handler
async show({ params, serialize }: HttpContext) {
  const post = await this.postService.findOrFail(params.id) // throws E_ROW_NOT_FOUND
  return serialize({ post: PostTransformer.transform(post) })
}

// ✅ Acceptable — only when you need context-specific recovery
async store({ request, response }: HttpContext) {
  try {
    const payload = await request.validateUsing(createPostValidator)
    const post = await this.postService.create(payload)
    return response.status(201).json({ post })
  } catch (error) {
    if (error.code === 'E_DUPLICATE_SLUG') {
      return response.conflict({ error: 'Slug already taken' })
    }
    throw error // re-throw unknown errors
  }
}
```

---

## 3. Services

Services hold all business logic. They are plain TypeScript classes resolved via the IoC container.

### Service vs Plain Function vs Repository

| Use | When |
| :--- | :--- |
| Service class | State is needed (injected deps), logic spans multiple models |
| Plain function | Pure transformation, no deps, could be in `#helpers/*` |
| Repository | When you want to abstract Lucid queries for testability or swap ORM |

**Recommendation:** Use service classes with DI. Skip the repository pattern unless you have > 1 data source or you're writing a library. Lucid's query builder is expressive enough.

### DI with the IoC Container in v7

```typescript
// app/services/post_service.ts
import { inject } from '@adonisjs/core'
import Post from '#models/post'
import type { CreatePostPayload, UpdatePostPayload } from '#validators/post_validator'
import MarkdownService from '#services/markdown_service'

@inject()
export default class PostService {
  constructor(private markdownService: MarkdownService) {}

  async paginate(page: number, perPage = 20) {
    return Post.query()
      .orderBy('created_at', 'desc')
      .paginate(page, perPage)
  }

  async findOrFail(id: string | number) {
    return Post.findOrFail(id)
  }

  async create(payload: CreatePostPayload) {
    const html = await this.markdownService.render(payload.body)
    return Post.create({
      ...payload,
      bodyHtml: html,
      slug: this.generateSlug(payload.title),
    })
  }

  async update(id: string | number, payload: UpdatePostPayload) {
    const post = await Post.findOrFail(id)
    if (payload.body) {
      payload = { ...payload, bodyHtml: await this.markdownService.render(payload.body) }
    }
    post.merge(payload)
    await post.save()
    return post
  }

  async delete(id: string | number) {
    const post = await Post.findOrFail(id)
    await post.delete()
  }

  private generateSlug(title: string): string {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
  }
}
```

**Critical v7 IoC rule:** `@inject()` on the class — not the constructor. AdonisJS reads the class decorator to wire dependencies. Never `new PostService()` directly.

---

## 4. Validators

VineJS is the validation layer. Define validators in `app/validators/`, export typed inferred types alongside them.

### v6 → v7 Validation Changes

| Feature | v6 | v7 |
| :--- | :--- | :--- |
| Framework | `@adonisjs/validator` with schema classes | VineJS (`@vinejs/vine`) |
| Modifiers | `BaseModifiers` class available | `BaseModifiers` removed in VineJS v4 |
| Usage | `request.validate(CreatePostValidator)` | `request.validateUsing(createPostValidator)` |
| Error key | Validation errors under `errors` flash key | Errors now under `inputErrorsBag` only |

### Complete Validator with Custom Messages

```typescript
// app/validators/post_validator.ts
import vine, { Infer } from '@vinejs/vine'

// ── Create ──────────────────────────────────────────────────────────────────

export const createPostValidator = vine.compile(
  vine.object({
    title: vine
      .string()
      .trim()
      .minLength(3)
      .maxLength(200),

    slug: vine
      .string()
      .trim()
      .regex(/^[a-z0-9-]+$/)
      .unique(async (db, value) => {
        const row = await db.from('posts').where('slug', value).first()
        return !row
      }),

    body: vine
      .string()
      .trim()
      .minLength(10),

    status: vine
      .enum(['draft', 'published', 'archived'] as const),

    tags: vine
      .array(vine.string().trim().maxLength(50))
      .maxLength(10)
      .optional(),

    publishedAt: vine
      .date({ formats: ['YYYY-MM-DD'] })
      .afterOrEqualToToday()
      .optional(),
  })
)

// ── Update (all fields optional) ────────────────────────────────────────────

export const updatePostValidator = vine.compile(
  vine.object({
    title: vine.string().trim().minLength(3).maxLength(200).optional(),
    body:  vine.string().trim().minLength(10).optional(),
    status: vine.enum(['draft', 'published', 'archived'] as const).optional(),
    tags: vine.array(vine.string().trim()).maxLength(10).optional(),
  })
)

// ── Query params validator ───────────────────────────────────────────────────

export const listPostsValidator = vine.compile(
  vine.object({
    page:   vine.number().min(1).optional(),
    status: vine.enum(['draft', 'published', 'archived'] as const).optional(),
    search: vine.string().trim().maxLength(100).optional(),
  })
)

// ── Infer TypeScript types ──────────────────────────────────────────────────
// Use these types in service method signatures — never re-type manually

export type CreatePostPayload  = Infer<typeof createPostValidator>
export type UpdatePostPayload  = Infer<typeof updatePostValidator>
export type ListPostsPayload   = Infer<typeof listPostsValidator>
```

### Custom Error Messages (per-validator)

```typescript
export const createPostValidator = vine.compile(
  vine.object({
    title: vine.string().minLength(3),
    slug:  vine.string().regex(/^[a-z0-9-]+$/),
  })
)

createPostValidator.messagesProvider = new SimpleMessagesProvider({
  'required':              'The {{ field }} field is required.',
  'string':                'The {{ field }} must be a string.',
  'minLength':             'The {{ field }} must be at least {{ min }} characters.',
  'title.minLength':       'Post title needs at least {{ min }} characters.',
  'slug.regex':            'Slug can only contain lowercase letters, numbers, and hyphens.',
})
```

### Using Validators for Query Params and Route Params

```typescript
// In controller — typed query params
async index({ request }: HttpContext) {
  const payload = await request.validateUsing(listPostsValidator, {
    data: request.qs(), // validate query string
  })
  // payload is fully typed as ListPostsPayload
}
```

---

## 5. TypeScript Patterns

### `tsconfig.json` for AdonisJS 7.x

```json
{
  "extends": "@adonisjs/tsconfig/tsconfig.app.json",
  "compilerOptions": {
    "rootDir": "./",
    "outDir": "./build",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

`@adonisjs/tsconfig/tsconfig.app.json` already enables: `strict`, `esModuleInterop`, `moduleResolution: bundler`, `target: ESNext`, `module: NodeNext`.

### Typing Request Bodies, Query Params, Route Params

```typescript
import type { HttpContext } from '@adonisjs/core/http'
import type { InferRouteParams } from '@adonisjs/core/helpers/types'
import { createPostValidator, ListPostsPayload } from '#validators/post_validator'

// Route params — use the v7 type helper
type PostRouteParams = InferRouteParams<'/posts/:id'>
// → { id: string }

// Request body — always derive from validator, never hand-write
type CreateBody = Infer<typeof createPostValidator>

export default class PostsController {
  async show({ params }: HttpContext) {
    // params.id is string — cast to number explicitly
    const id = Number(params.id)
    if (Number.isNaN(id)) throw new Error('Invalid ID')
  }

  async index({ request }: HttpContext) {
    const qs = await request.validateUsing(listPostsValidator, {
      data: request.qs(),
    })
    // qs: ListPostsPayload — fully typed
  }
}
```

### Interface vs Type — Convention

Use **interface** for object shapes that describe entities or contracts (models, DTOs, service boundaries). Use **type** for unions, intersections, and utility derivations (validator inferences, mapped types).

```typescript
// ✅ interface — for entity/contract shapes
interface PostMeta {
  readingTime: number
  wordCount: number
  tags: string[]
}

// ✅ type — for derived/union types
type PostStatus = 'draft' | 'published' | 'archived'
type CreatePostPayload = Infer<typeof createPostValidator>
type ApiResponse<T> = { data: T; meta?: PostMeta }
```

### Avoiding `any` — Patterns for Unknown API Responses

```typescript
import { z } from 'zod' // or use VineJS for runtime validation

// Pattern 1: Zod parse on external API responses
const OpenAIChunkSchema = z.object({
  choices: z.array(z.object({
    delta: z.object({ content: z.string().optional() }),
    finish_reason: z.string().nullable(),
  })),
})

type OpenAIChunk = z.infer<typeof OpenAIChunkSchema>

async function parseChunk(raw: unknown): Promise<OpenAIChunk> {
  return OpenAIChunkSchema.parse(raw)
}

// Pattern 2: Type guard for JSON parsing
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

// Pattern 3: satisfies operator to validate against interface without widening
const config = {
  model: 'llama-3.3-70b',
  temperature: 0.7,
} satisfies LLMConfig
```

### Fully Typed Controller + Service Interaction

```typescript
// app/controllers/posts_controller.ts
import type { HttpContext } from '@adonisjs/core/http'
import { inject } from '@adonisjs/core'
import { createPostValidator, updatePostValidator } from '#validators/post_validator'
import PostService from '#services/post_service'
import PostTransformer from '#transformers/post_transformer'

@inject()
export default class PostsController {
  constructor(private readonly posts: PostService) {}

  async store({ request, response, serialize }: HttpContext) {
    // payload: CreatePostPayload — inferred from validator, not hand-typed
    const payload = await request.validateUsing(createPostValidator)
    const post = await this.posts.create(payload)
    return response.status(201).send(serialize({
      post: PostTransformer.transform(post),
    }))
  }
}
```

---

## 6. Server-Sent Events (SSE)

For pub/sub broadcast SSE, use Transmit (`@adonisjs/transmit`). For streaming LLM responses (where YOU control the stream), write a raw SSE controller directly — Transmit is not designed for request-scoped streaming.

### Raw SSE for LLM Streaming

```typescript
// app/controllers/stream_controller.ts
import type { HttpContext } from '@adonisjs/core/http'
import { inject } from '@adonisjs/core'
import LlmService from '#services/llm_service'

@inject()
export default class StreamController {
  constructor(private llm: LlmService) {}

  async chat({ request, response }: HttpContext) {
    // 1. Parse + validate input
    const { prompt, model } = request.only(['prompt', 'model']) as {
      prompt: string
      model: string
    }

    if (!prompt?.trim()) {
      return response.badRequest({ error: 'prompt is required' })
    }

    // 2. Set SSE headers BEFORE writing anything
    response.header('Content-Type',  'text/event-stream')
    response.header('Cache-Control', 'no-cache, no-transform')
    response.header('Connection',    'keep-alive')
    response.header('X-Accel-Buffering', 'no') // disable Nginx buffering

    // 3. Get the underlying Node.js ServerResponse
    const res = response.response

    // 4. Handle client disconnect — critical for preventing memory leaks
    let aborted = false
    const abortController = new AbortController()

    request.request.on('close', () => {
      aborted = true
      abortController.abort()
    })

    // 5. Helper to write SSE frames
    const sendEvent = (data: string, event?: string): boolean => {
      if (aborted || res.destroyed) return false
      if (event) res.write(`event: ${event}\n`)
      res.write(`data: ${data}\n\n`)
      return true
    }

    // 6. Stream from llama.cpp / OpenAI-compatible endpoint
    try {
      const stream = await this.llm.streamChat({
        prompt,
        model: model ?? 'llama-3.3-70b',
        signal: abortController.signal,
      })

      for await (const chunk of stream) {
        if (aborted) break

        const delta = chunk.choices[0]?.delta?.content
        if (delta) {
          sendEvent(JSON.stringify({ delta }))
        }

        if (chunk.choices[0]?.finish_reason === 'stop') {
          sendEvent(JSON.stringify({ done: true }), 'done')
          break
        }
      }
    } catch (error) {
      if (!aborted) {
        sendEvent(JSON.stringify({ error: 'Stream error' }), 'error')
      }
    } finally {
      if (!res.destroyed) {
        res.end()
      }
    }
  }
}
```

```typescript
// app/services/llm_service.ts
import { z } from 'zod'

const ChunkSchema = z.object({
  choices: z.array(z.object({
    delta: z.object({ content: z.string().optional() }).optional(),
    finish_reason: z.string().nullable().optional(),
  })),
})

export default class LlmService {
  private readonly baseUrl: string

  constructor() {
    this.baseUrl = process.env.LLM_BASE_URL ?? 'http://localhost:8080'
  }

  async *streamChat(opts: {
    prompt: string
    model: string
    signal: AbortSignal
  }): AsyncGenerator<z.infer<typeof ChunkSchema>> {
    const res = await fetch(`${this.baseUrl}/v1/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: opts.model,
        messages: [{ role: 'user', content: opts.prompt }],
        stream: true,
      }),
      signal: opts.signal,
    })

    if (!res.ok || !res.body) {
      throw new Error(`LLM returned ${res.status}`)
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder()

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const lines = decoder.decode(value).split('\n')
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6).trim()
          if (raw === '[DONE]') return
          try {
            yield ChunkSchema.parse(JSON.parse(raw))
          } catch {
            // malformed chunk — skip
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  }
}
```

**Memory leak prevention checklist:**

*   Always attach `request.request.on('close', ...)` and set an abort flag
*   Pass `AbortSignal` to `fetch()` so in-flight HTTP to llama.cpp is cancelled
*   Call `res.end()` in `finally` — never leave an open stream
*   Check `res.destroyed` before writing to avoid "write after end" errors

---

## 7. File System Operations

Use Node's native `fs/promises` directly — no wrapper needed. Reserve `@adonisjs/drive` for user-uploaded files that need multi-driver support (local/S3/GCS). For markdown data sources, use `edge-markdown` or a service reading raw files.

### Async File Operations with Strict Error Handling

```typescript
// app/services/markdown_service.ts
import { readFile, readdir, stat } from 'node:fs/promises'
import { join, extname, basename } from 'node:path'
import matter from 'gray-matter'            // frontmatter parsing
import { marked } from 'marked'             // markdown → HTML

interface PostFrontmatter {
  title: string
  date: string
  tags?: string[]
  draft?: boolean
}

interface ParsedPost {
  slug: string
  frontmatter: PostFrontmatter
  html: string
  excerpt: string
  readingTime: number
}

export default class MarkdownService {
  private readonly contentDir: string

  constructor() {
    // import.meta.dirname — v7 replaces getDirname() helper
    this.contentDir = join(import.meta.dirname, '..', '..', 'content', 'posts')
  }

  async getPost(slug: string): Promise<ParsedPost> {
    const filePath = join(this.contentDir, `${slug}.md`)

    // Explicit error handling — never swallow fs errors silently
    let raw: string
    try {
      raw = await readFile(filePath, 'utf-8')
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        throw Object.assign(new Error(`Post not found: ${slug}`), {
          code: 'E_POST_NOT_FOUND',
          status: 404,
        })
      }
      throw error
    }

    return this.parse(slug, raw)
  }

  async listPosts(): Promise<ParsedPost[]> {
    let files: string[]
    try {
      files = await readdir(this.contentDir)
    } catch {
      return []
    }

    const posts = await Promise.all(
      files
        .filter((f) => extname(f) === '.md')
        .map(async (f) => {
          const slug = basename(f, '.md')
          return this.getPost(slug)
        })
    )

    return posts
      .filter((p) => !p.frontmatter.draft)
      .sort((a, b) =>
        new Date(b.frontmatter.date).getTime() -
        new Date(a.frontmatter.date).getTime()
      )
  }

  async render(markdownText: string): Promise<string> {
    return marked.parse(markdownText)
  }

  private parse(slug: string, raw: string): ParsedPost {
    const { data, content } = matter(raw)

    // Validate frontmatter shape at runtime
    if (typeof data.title !== 'string' || typeof data.date !== 'string') {
      throw new Error(`Post "${slug}" is missing required frontmatter fields`)
    }

    const fm = data as PostFrontmatter
    const html = marked.parse(content) as string
    const words = content.split(/\s+/).length
    const excerpt = content.replace(/[#*`[\]]/g, '').slice(0, 200).trim()

    return {
      slug,
      frontmatter: fm,
      html,
      excerpt,
      readingTime: Math.ceil(words / 200),
    }
  }
}
```

**Rules:**

*   Use `import.meta.dirname` — `getDirname()` was removed in v7
*   Check `error.code === 'ENOENT'` before constructing 404 errors
*   Never use synchronous `readFileSync` in request handlers
*   Use `Promise.all()` for parallel file reads, not sequential `await` in loops

---

## 8. HTMX + Edge.js Integration

**The pattern:** detect `HX-Request` header → return a partial template; otherwise return the full layout.

### Detecting HTMX and Returning Partials vs Full Pages

```typescript
// app/controllers/blog_controller.ts
import type { HttpContext } from '@adonisjs/core/http'
import { inject } from '@adonisjs/core'
import MarkdownService from '#services/markdown_service'

@inject()
export default class BlogController {
  constructor(private markdown: MarkdownService) {}

  async index({ request, view }: HttpContext) {
    const posts = await this.markdown.listPosts()
    const isHtmx = !!request.header('HX-Request')

    if (isHtmx) {
      // Return only the list partial — HTMX will swap it in
      return view.render('blog/_post_list', { posts })
    }
    return view.render('blog/index', { posts })
  }

  async show({ params, request, view, response }: HttpContext) {
    const post = await this.markdown.getPost(params.slug)
    const isHtmx = !!request.header('HX-Request')

    if (isHtmx) {
      // Push browser URL for HTMX history support
      response.header('HX-Push-Url', `/blog/${params.slug}`)
      return view.render('blog/_post_detail', { post })
    }
    return view.render('blog/show', { post })
  }
}
```

### Edge.js Template Structure

```xml
{{-- resources/views/blog/index.edge --}}
@layout('layouts/app')

@section('body')
  <div id="content-area"
       hx-boost="true">
    @include('blog/_post_list')
  </div>
@end
```

```xml
{{-- resources/views/blog/_post_list.edge (partial) --}}
<ul id="post-list">
  @each(post in posts)
    <li>
      <a href="/blog/{{ post.slug }}"
         hx-get="/blog/{{ post.slug }}"
         hx-target="#content-area"
         hx-swap="innerHTML"
         hx-push-url="true">
        {{ post.frontmatter.title }}
      </a>
    </li>
  @end
</ul>
```

### OOB (Out-of-Band) Swaps

```typescript
// Controller — returning multiple DOM targets in one response
async toggleFavorite({ params, request, view, response }: HttpContext) {
  const post = await this.postService.toggleFavorite(params.id)
  const isHtmx = !!request.header('HX-Request')

  if (!isHtmx) return response.redirect('/blog')

  // Primary swap: the button itself
  // OOB swap: update the favorites counter in the nav
  const primary = await view.render('blog/_favorite_button', { post })
  const oob     = await view.render('blog/_nav_favorites_count', { post })

  return response.send(primary + oob)
}
```

```xml
{{-- resources/views/blog/_nav_favorites_count.edge --}}
<span id="favorites-count"
      hx-swap-oob="true">
  {{ favoritesCount }}
</span>
```

**Key rules:**

*   Always use `hx-push-url="true"` or `HX-Push-Url` header — never let HTMX navigation break the URL bar
*   OOB swaps require `hx-swap-oob="true"` on the element and the element's id must exist in the DOM
*   For full-page vs partial detection, prefer checking `request.header('HX-Request')` in the controller over a middleware, so logic stays co-located

---

## 9. Alpine.js Integration

Alpine.js component definitions belong inline in Edge templates for simple components and in dedicated JS files under `resources/js/` for reusable ones. Never define Alpine data in PHP-style global `x-data` strings longer than 3 properties — extract to a file.

### Dropdown Component

```xml
{{-- resources/views/components/dropdown.edge --}}
<div x-data="dropdown()"
     x-on:keydown.escape="close()"
     class="relative">

  <button x-on:click="toggle()"
          x-bind:aria-expanded="isOpen">
    {{ trigger }}
  </button>

  <ul x-show="isOpen"
      x-transition
      x-on:click.outside="close()"
      class="absolute z-10 bg-white shadow-lg">
    {{{ content }}}
  </ul>
</div>
```

```javascript
// resources/js/components/dropdown.ts
export function dropdown() {
  return {
    isOpen: false as boolean,
    toggle(): void { this.isOpen = !this.isOpen },
    open(): void   { this.isOpen = true },
    close(): void  { this.isOpen = false },
  }
}
```

### Communicating Between Alpine.js and HTMX

Use HTMX events (`htmx:afterSwap`, `htmx:beforeSwap`) to trigger Alpine re-initialization, and Alpine `$dispatch` to send events that HTMX can listen to.

```xml
{{-- A component that reacts to HTMX swap events --}}
<div x-data="postsFilter()"
     x-on:htmx:after-swap.window="onSwapComplete($event)">

  {{-- Filter triggers HTMX request --}}
  <select name="status"
          hx-get="/posts"
          hx-target="#posts-container"
          hx-trigger="change"
          hx-include="[name='search']"
          x-on:change="setLoading(true)">
    <option value="">All</option>
    <option value="published">Published</option>
    <option value="draft">Draft</option>
  </select>

  {{-- Loading indicator driven by Alpine state --}}
  <span x-show="loading" x-cloak>Loading…</span>

  <div id="posts-container">
    @include('posts/_list')
  </div>
</div>

<script type="module">
import { postsFilter } from '/js/components/posts_filter.js'
document.addEventListener('alpine:init', () => {
  Alpine.data('postsFilter', postsFilter)
})
</script>
```

```typescript
// resources/js/components/posts_filter.ts
export function postsFilter() {
  return {
    loading: false as boolean,
    setLoading(val: boolean): void { this.loading = val },
    onSwapComplete(_event: CustomEvent): void {
      this.loading = false
    },
  }
}
```

---

## 10. Environment Configuration

v7 replaces `dotenv` with Node's native `util.parseEnv`. The `Env.create()` pattern from v6 is unchanged in API but gains `schema.secret()` type.

### `start/env.ts` — Complete Validation Block

```typescript
// start/env.ts
import { Env } from '@adonisjs/core/env'

export default await Env.create(new URL('../', import.meta.url), {

  // ── App ────────────────────────────────────────────────────────────────
  NODE_ENV: Env.schema.enum(['development', 'production', 'test'] as const),
  PORT:     Env.schema.number(),
  APP_KEY:  Env.schema.secret(),          // ← NEW in v7: Secret type hides value in logs
  APP_NAME: Env.schema.string(),
  LOG_LEVEL: Env.schema.enum(['trace', 'debug', 'info', 'warn', 'error', 'fatal'] as const),

  // ── Database ────────────────────────────────────────────────────────────
  DB_HOST:     Env.schema.string(),
  DB_PORT:     Env.schema.number(),
  DB_USER:     Env.schema.string(),
  DB_PASSWORD: Env.schema.secret(),
  DB_DATABASE: Env.schema.string(),

  // ── External API ─────────────────────────────────────────────────────────
  // Docker Secret file support: LLM_API_KEY=file:/run/secrets/llm_key
  LLM_BASE_URL: Env.schema.string.optional(),
  LLM_API_KEY:  Env.schema.secret.optional(),

  // ── Mail ─────────────────────────────────────────────────────────────────
  MAIL_FROM_ADDRESS: Env.schema.string(),
  MAIL_FROM_NAME:    Env.schema.string(),
  SMTP_HOST:   Env.schema.string.optional(),
  SMTP_PORT:   Env.schema.number.optional(),

  // ── Session ───────────────────────────────────────────────────────────────
  SESSION_DRIVER: Env.schema.enum(['cookie', 'redis', 'memory'] as const),
})
```

### Accessing Config in Services (NOT Controllers)

```typescript
// config/llm.ts — define once, import everywhere
import env from '#start/env'
import { defineConfig } from '@adonisjs/core/app'

const llmConfig = {
  baseUrl:  env.get('LLM_BASE_URL') ?? 'http://localhost:8080',
  // .release() unwraps the Secret value — only call in service initialization
  apiKey:   env.get('LLM_API_KEY')?.release(),
  timeout:  30_000,
} as const

export default llmConfig

// app/services/llm_service.ts
import llmConfig from '#config/llm'

export default class LlmService {
  private readonly baseUrl = llmConfig.baseUrl  // ✅ From config, not env directly
}
```

**Rule:** Services import from `#config/*`. Controllers never touch env or config directly — that is a service/config concern.

### v6 → v7 Env Changes

*   `dotenv` dependency removed; parsing is native
*   `APP_KEY` no longer used for encryption (moved to `config/encryption.ts`)
*   New `schema.secret()` type — use for all API keys, tokens, passwords
*   New file: modifier: `GCS_KEY=file:/run/secrets/gcs_key`

---

## 11. Error Handling

v7 fixes a long-standing bug: status pages are skipped for JSON Accept header requests. API clients now always get JSON errors.

### Custom Exception Handler

```typescript
// app/exceptions/handler.ts
import { ExceptionHandler, HttpContext } from '@adonisjs/core/http'
import type { StatusPageRange, StatusPageRenderer } from '@adonisjs/core/types/http'
import app from '@adonisjs/core/services/app'
import logger from '@adonisjs/core/services/logger'

export default class HttpExceptionHandler extends ExceptionHandler {
  // Render these Edge views for non-JSON requests
  protected statusPages: Record<StatusPageRange, StatusPageRenderer> = {
    '404':     (error, { view }) => view.render('errors/not_found', { error }),
    '422':     (error, { view }) => view.render('errors/validation', { error }),
    '500..599':(error, { view }) => view.render('errors/server_error', { error }),
  }

  protected debug = !app.inProduction

  async handle(error: unknown, ctx: HttpContext) {
    // Custom domain error → structured response
    if (error instanceof AppException) {
      return this.handleAppException(error, ctx)
    }

    // Let the parent handle E_VALIDATION_ERROR, E_ROW_NOT_FOUND, etc.
    return super.handle(error, ctx)
  }

  private async handleAppException(error: AppException, ctx: HttpContext) {
    const { request, response, view } = ctx
    const isHtmx = !!request.header('HX-Request')
    const wantsJson = request.accepts(['html', 'application/json']) === 'application/json'

    if (wantsJson) {
      return response.status(error.status).json({
        error: error.message,
        code:  error.code,
      })
    }

    if (isHtmx) {
      // Tell HTMX to retarget the error into a toast element
      response.header('HX-Retarget', '#toast-container')
      response.header('HX-Reswap',   'innerHTML')
      return response
        .status(error.status)
        .send(await view.render('partials/_toast', {
          type:    'error',
          message: error.message,
        }))
    }

    return response
      .status(error.status)
      .redirect(`/error?code=${error.code}`)
  }

  async report(error: unknown, ctx: HttpContext) {
    if (error instanceof AppException && error.status < 500) return
    logger.error({ err: error, url: ctx.request.url() }, 'Unhandled exception')
  }
}
```

### Custom Application Exception

```typescript
// app/exceptions/app_exception.ts
export default class AppException extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly status: number = 400
  ) {
    super(message)
    this.name = 'AppException'
  }

  static notFound(resource: string) {
    return new AppException(`${resource} not found`, 'E_NOT_FOUND', 404)
  }

  static forbidden(action: string) {
    return new AppException(`Not allowed to ${action}`, 'E_FORBIDDEN', 403)
  }
}
```

---

## 12. Testing with Japa

AdonisJS v7 uses Japa with `@japa/plugin-adonisjs`. Functional tests boot the full HTTP server; unit tests do not.

### Complete Functional Test

```typescript
// tests/functional/posts/show.spec.ts
import { test }       from '@japa/runner'
import testUtils      from '@adonisjs/core/services/test_utils'
import app            from '@adonisjs/core/services/app'
import sinon          from 'sinon'
import MarkdownService from '#services/markdown_service'

test.group('GET /blog/:slug', (group) => {
  // Migrate and rollback DB around each test
  group.each.setup(() => testUtils.db().withGlobalTransaction())

  group.teardown(async () => sinon.restore())

  test('returns full page for regular request', async ({ client, assert }) => {
    const response = await client.get('/blog/hello-world')

    response.assertStatus(200)
    response.assertBodyContains('Hello World')   // asserting HTML body text
  })

  test('returns partial for HTMX request', async ({ client, assert }) => {
    const response = await client
      .get('/blog/hello-world')
      .header('HX-Request', 'true')

    response.assertStatus(200)
    // Partial should NOT contain full layout wrapper
    response.assertBodyNotContains('<!DOCTYPE html>')
    response.assertBodyContains('class="post-detail"')
  })

  test('returns 404 for unknown slug', async ({ client }) => {
    const response = await client.get('/blog/does-not-exist')
    response.assertStatus(404)
  })

  test('mocks file system and external LLM call', async ({ client }) => {
    // Mock MarkdownService to avoid real file I/O
    const fakePosts = [{
      slug: 'test-post',
      frontmatter: { title: 'Test Post', date: '2026-01-01' },
      html: '<p>Content</p>',
      excerpt: 'Content',
      readingTime: 1,
    }]

    sinon
      .stub(MarkdownService.prototype, 'listPosts')
      .resolves(fakePosts)

    // Swap container binding for LlmService
    app.container.swap(LlmService, () => ({
      streamChat: async function* () {
        yield { choices: [{ delta: { content: 'Hello' }, finish_reason: null }] }
      },
    }))

    const response = await client.get('/blog')
    response.assertStatus(200)
    response.assertBodyContains('Test Post')

    app.container.restore(LlmService)
  })
})
```

### Unit Test for a Service

```typescript
// tests/unit/markdown_service.spec.ts
import { test } from '@japa/runner'
import MarkdownService from '#services/markdown_service'
import { tmpdir } from 'node:os'
import { writeFile, mkdir } from 'node:fs/promises'
import { join } from 'node:path'

test.group('MarkdownService', () => {
  test('parses frontmatter and returns structured post', async ({ assert }) => {
    const tmp = join(tmpdir(), `adonis-test-${Date.now()}`)
    await mkdir(tmp, { recursive: true })
    await writeFile(join(tmp, 'my-post.md'), `---
title: My Post
date: 2026-04-01
---
Hello world content here.
`)

    const service = new MarkdownService()
    // @ts-expect-error: override private for test
    service.contentDir = tmp

    const post = await service.getPost('my-post')

    assert.equal(post.frontmatter.title, 'My Post')
    assert.include(post.html, 'Hello world content here')
  })

  test('throws E_POST_NOT_FOUND for missing file', async ({ assert }) => {
    const service = new MarkdownService()
    await assert.rejects(
      () => service.getPost('nonexistent'),
      (err) => (err as { code: string }).code === 'E_POST_NOT_FOUND'
    )
  })
})
```

---

## 13. Routing in v7

v7 auto-generates route names from the `ControllerName.method` pattern and generates barrel files.

### Complete Routes File

```typescript
// start/routes.ts
import router from '@adonisjs/core/services/router'
import { middleware } from '#start/kernel'
import { controllers } from '#generated/controllers'  // v7 barrel — no manual lazy imports

// ── Public routes ──────────────────────────────────────────────────────────
router.get('/', [controllers.Home, 'index'])          // → home.index
router.get('/blog', [controllers.Blog, 'index'])      // → blog.index
router.get('/blog/:slug', [controllers.Blog, 'show']) // → blog.show

// ── Auth routes ────────────────────────────────────────────────────────────
router.group(() => {
  router.get('/login',  [controllers.Session, 'create'])  // → session.create
  router.post('/login', [controllers.Session, 'store'])   // → session.store
  router.delete('/logout', [controllers.Session, 'destroy']) // → session.destroy
  router.get('/register', [controllers.Register, 'create'])
  router.post('/register', [controllers.Register, 'store'])
}).prefix('/auth')

// ── Protected routes ───────────────────────────────────────────────────────
router
  .group(() => {
    // Resource: GET/POST/PATCH/DELETE for posts
    router.resource('posts', controllers.Posts)
      .only(['index', 'show', 'create', 'store', 'edit', 'update', 'destroy'])

    // HTMX-specific partials — explicit routes, not resource
    router.get('/posts/:id/preview', [controllers.Posts, 'preview'])
    router.post('/posts/:id/publish', [controllers.Posts, 'publish'])

    // LLM Streaming
    router.post('/ai/chat', [controllers.AiChat, 'stream'])
  })
  .prefix('/app')
  .middleware([middleware.auth()])

// ── API routes ─────────────────────────────────────────────────────────────
router
  .group(() => {
    router.resource('api/v1/posts', controllers.Api.Posts)
      .apiOnly()
  })
  .middleware([middleware.auth({ guards: ['api'] })])
  .prefix('/api/v1')
```

**Resource vs manual:** Use `router.resource()` when a controller follows all 7 RESTful actions. Use manual routes for any deviation — don't override resource routes with `.only()` chains just to add a non-standard action.

---

## 14. Middleware

v7 introduces `start/kernel.ts` as the canonical middleware registration file.

### Built-in vs Custom Middleware

| Built-in | Purpose |
| :--- | :--- |
| `@adonisjs/core/bodyparser_middleware` | Parse JSON, multipart, form body |
| `@adonisjs/session/session_middleware` | Session management |
| `@adonisjs/auth/auth_middleware` | Authentication guard |
| `@adonisjs/shield/shield_middleware` | CSRF, XSS headers |
| `@adonisjs/inertia/inertia_middleware` | Inertia shared props |

### Custom Middleware — API Key Header Validation

```typescript
// app/middleware/api_key_middleware.ts
import type { HttpContext } from '@adonisjs/core/http'
import type { NextFn } from '@adonisjs/core/types/http'
import env from '#start/env'

export default class ApiKeyMiddleware {
  async handle({ request, response }: HttpContext, next: NextFn): Promise<void> {
    const providedKey = request.header('X-Api-Key')

    if (!providedKey) {
      response.unauthorized({ error: 'Missing X-Api-Key header' })
      return
    }

    // Constant-time comparison to prevent timing attacks
    const validKey  = env.get('INTERNAL_API_KEY').release()
    if (!this.safeCompare(providedKey, validKey)) {
      response.unauthorized({ error: 'Invalid API key' })
      return
    }

    await next()
  }

  private safeCompare(a: string, b: string): boolean {
    if (a.length !== b.length) return false
    let result = 0
    for (let i = 0; i < a.length; i++) {
      result |= a.charCodeAt(i) ^ b.charCodeAt(i)
    }
    return result === 0
  }
}
```

```typescript
// start/kernel.ts — registration
import router from '@adonisjs/core/services/router'
import server from '@adonisjs/core/services/server'

server.use([
  () => import('@adonisjs/core/bodyparser_middleware'),
  () => import('@adonisjs/session/session_middleware'),
  () => import('@adonisjs/shield/shield_middleware'),
])

export const middleware = router.named({
  auth:   () => import('@adonisjs/auth/auth_middleware'),
  apiKey: () => import('#middleware/api_key_middleware'),
})
```

### File-Based Auth Without a Database

```typescript
// app/middleware/static_token_middleware.ts
import type { HttpContext } from '@adonisjs/core/http'
import type { NextFn } from '@adonisjs/core/types/http'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'

interface TokenRecord {
  token: string
  user: string
  scopes: string[]
}

export default class StaticTokenMiddleware {
  private tokens: TokenRecord[] | null = null

  async handle({ request, response }: HttpContext, next: NextFn): Promise<void> {
    const authHeader = request.header('Authorization') ?? ''
    const token = authHeader.replace(/^Bearer\s+/i, '').trim()

    if (!token) {
      return response.unauthorized({ error: 'Authorization header required' })
    }

    const tokens = await this.loadTokens()
    const record = tokens.find((t) => t.token === token)

    if (!record) {
      return response.unauthorized({ error: 'Invalid token' })
    }

    // Attach user to request for downstream use
    request.updateBody({ ...request.body(), _authUser: record.user })
    await next()
  }

  private async loadTokens(): Promise<TokenRecord[]> {
    if (this.tokens) return this.tokens // singleton cache
    const raw = await readFile(
      join(import.meta.dirname, '..', '..', 'config', 'tokens.json'),
      'utf-8'
    )
    this.tokens = JSON.parse(raw) as TokenRecord[]
    return this.tokens
  }
}
```

---

## 15. Anti-Patterns to Avoid

### Top 10 Anti-Patterns in AdonisJS 7.x

1.  **Using `router.makeUrl()`** — deprecated in v7
    ```typescript
    // ❌ v6 / deprecated v7
    router.makeUrl('posts.show', { id: 1 })

    // ✅ v7 — type-safe
    import { urlFor } from '@adonisjs/core/services/url_builder'
    urlFor('posts.show', { id: 1 })
    ```
2.  **Manually writing lazy controller imports**
    ```typescript
    // ❌ v6 pattern — never do this in v7
    const PostsController = () => import('#controllers/posts_controller')
    router.get('/posts', [PostsController, 'index'])

    // ✅ v7 — use generated barrel
    import { controllers } from '#generated/controllers'
    router.get('/posts', [controllers.Posts, 'index'])
    ```
3.  **Reading errors from flash messages**
    ```xml
    {{-- ❌ v6 — removed in v7 --}}
    {{ flashMessages.get('errors.email') }}

    {{-- ✅ v7 --}}
    {{ flashMessages.get('inputErrorsBag.email') }}
    ```
4.  **Using `getDirname()` / `getFilename()` helpers**
    ```typescript
    // ❌ removed in v7
    import { getDirname } from '@adonisjs/core/helpers'
    const dir = getDirname()

    // ✅ v7 — native Node.js
    const dir = import.meta.dirname
    ```
5.  **Using CUID**
    ```typescript
    // ❌ removed in v7
    import { cuid } from '@adonisjs/core/helpers'

    // ✅ v7
    const id = crypto.randomUUID()
    ```
6.  **Business logic in controllers (fat controller)**
    ```typescript
    // ❌ fat controller
    async store({ request, response }: HttpContext) {
      const data = request.only(['title', 'body'])
      const slug = data.title.toLowerCase().replace(/ /g, '-')
      const html = await marked(data.body)
      const post = await Post.create({ ...data, slug, bodyHtml: html })
      await Mail.send(/* welcome email */)
      return response.json({ post })
    }

    // ✅ thin controller — delegate all logic
    async store({ request, response, serialize }: HttpContext) {
      const payload = await request.validateUsing(createPostValidator)
      const post = await this.postService.create(payload)
      return response.status(201).send(serialize({ post: PostTransformer.transform(post) }))
    }
    ```
7.  **Returning raw model instances instead of transformers**
    ```typescript
    // ❌ v6 pattern — no type safety, leaks model internals
    return response.json({ post: post.serialize() })

    // ✅ v7 — use a Transformer
    return serialize({ post: PostTransformer.transform(post) })
    ```
8.  **Defining encryption config in `config/app.ts`**
    ```typescript
    // ❌ v6 (still compiles in v7 but ignored for encryption)
    export const appKey = env.get('APP_KEY')

    // ✅ v7 — dedicated encryption config
    // config/encryption.ts
    import { defineConfig, drivers } from '@adonisjs/core/encryption'
    export default defineConfig({
      default: 'aes256gcm',
      list: {
        aes256gcm: drivers.aes256gcm({ keys: [env.get('APP_KEY').release()] }),
      },
    })
    ```
9.  **Using `ts-node` / `ts-node-maintained`**
    ```typescript
    // ❌ v6 — removed in v7
    import 'ts-node-maintained/register/esm'

    // ✅ v7
    import '@poppinss/ts-exec'
    ```
10. **Using `onBuildStarting` assembler hook name**
    ```typescript
    // ❌ v6 hook names — TypeScript errors in v7
    { hooks: { onBuildStarting: [/* ... */] } }

    // ✅ v7 renamed hooks
    { hooks: { buildStarting: [() => import('@adonisjs/vite/build_hook')] } }
    ```

### Quick Reference: v6 → v7 Breaking Changes

| Area | v6 | v7 |
| :--- | :--- | :--- |
| Node.js | 20+ | 24+ required |
| JIT compiler | `ts-node-maintained` | `@poppinss/ts-exec` |
| Route URL builder | `router.makeUrl()` | `urlFor()` type-safe |
| Controller imports | Manual lazy `() => import()` | Generated barrel `#generated/controllers` |
| Route naming | Manual `.as('posts.index')` | Auto-generated from controller name |
| Serialization | `model.serialize()` | `PostTransformer.transform(post)` |
| Flash errors key | `errors.field` | `inputErrorsBag.field` |
| Request class | `Request` | `HttpRequest` |
| Encryption config | `config/app.ts appKey` | `config/encryption.ts` |
| `getDirname()` | Available | Removed → `import.meta.dirname` |
| CUID | Available | Removed → `crypto.randomUUID()` |
| `dotenv` | Runtime dependency | Replaced by `node:util.parseEnv` |
| Status pages | Returned for all requests | Skipped for JSON Accept header |
| Inertia shared data | `config/inertia.ts sharedData` | `InertiaMiddleware.share()` |
| Assembler hooks | `onBuildStarting` etc. | `buildStarting` etc. |
| Test glob pattern | `**/*.spec(.ts\|.js)` | `**/*.spec.{ts,js}` |

*Preparado con Claude Sonnet 4.6 Thinking*
