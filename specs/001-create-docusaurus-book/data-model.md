# Data Model

**Date**: 2025-12-07
**Context**: This document defines the data model for the digital textbook project, as derived from the feature specification.

## Entity Overview

The project's content is modeled around three core entities, which map directly to the file system structure within the Docusaurus `docs` directory.

### 1. Book

- **Description**: The top-level entity representing the entire textbook.
- **Implementation**: This is represented by the Docusaurus site itself and configured in `docusaurus.config.js`.

### 2. Chapter

- **Description**: A main section of the book, used to group related pages.
- **Implementation**: A chapter is represented by a subdirectory within the `docs` directory. The ordering and labeling of chapters are managed in `sidebars.js`.
- **Fields**:
    - `title`: The name of the chapter (defined in `sidebars.js` or front matter).
    - `pages`: A collection of `Page` entities.
- **Relationships**:
    - A `Book` has many `Chapter`s.
    - A `Chapter` has many `Page`s.

### 3. Page

- **Description**: A single article, tutorial, or section within a chapter.
- **Implementation**: A `Page` is a Markdown file (`.md` or `.mdx`) within a chapter's subdirectory (or at the top level).
- **Fields**:
    - `title`: The title of the page (from the Markdown H1 or front matter).
    - `content`: The body of the article, written in Markdown.
- **Relationships**:
    - A `Page` belongs to one `Chapter`.

## File System Representation

The relationship between these entities is physically represented by the directory structure:

```
docs/
├── chapter-1/              <-- Chapter
│   ├── page-1.md           <-- Page
│   └── page-2.md           <-- Page
├── chapter-2/              <-- Chapter
│   ├── overview.md         <-- Page
│   └── advanced-topic.md   <-- Page
└── intro.md                <-- Page (part of a default, top-level chapter)
```
