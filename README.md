# ImageScribe

ImageScribe generates natural-language descriptions of images using a Groq-hosted

vision model. Upload an image, pick a writing style, and get a ready-to-use

description — useful for alt text, e-commerce listings, SEO copy, or creative captions.


The project is split into two services:


- **Backend** — a FastAPI API that validates images, downscales them for cost,

  and calls the vision model via Groq.

- **Frontend** — a Streamlit app that provides the upload UI and talks to the backend.

---## Features

- Upload `JPG`, `JPEG`, `PNG`, or `WEBP` images.

- Five description styles (see table below).

- Robust validation: size limits, MIME checks, magic-byte detection, Pillow verification, and dimension limits.

- Automatic downscaling before sending to the model to reduce token cost.

- Per-IP rate limiting and request-size guards.

- Safe error handling, never raw tracebacks.

---## Description Styles

| Style              | Description                                       |

|--------------------|---------------------------------------------------|

| `Standard`         | Balanced, general-purpose description (default).  |

| `Short`            | Concise, one- or two-line summary.                |

| `Detailed`         | Thorough, in-depth description.                   |

| `SEO / E-commerce` | Product-focused copy optimised for listings.      |

| `Creative`         | Expressive, imaginative caption.                  |


```---## Prerequisites

- Python 3.10+

- A Groq API key (only required to actually generate descriptions).

---## Setup### 1. Backend```

cd imagescribe\backend

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

```

Create your environment file from the example and add your key:

```

copy .env.example .env

```

Then edit `.env`:

```

GROQ_API_KEY=gsk_...

GROQ_MODEL=qwen/qwen3.6-27b

MAX_FILE_SIZE_MB=10

MAX_IMAGE_EDGE_PX=1536

```> The API key is **optional at startup** — the backend boots without it. The key

> is only validated the first time you actually call the vision model.

### 2. Frontend

Open a **second terminal**:

```

cd imagescribe\frontend

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

```---## Running

Run the two services in separate terminals.

### Backend (terminal 1)```

cd imagescribe\backend

.\.venv\Scripts\Activate.ps1

uvicorn app.main:app --reload --port 8000

```

- Swagger UI: <http://localhost:8000/docs>

### Frontend (terminal 2)```

cd imagescribe\frontend

.\.venv\Scripts\Activate.ps1

streamlit run app.py

```

Open the URL Streamlit prints (usually <http://localhost:8501>), upload an image,

pick a style, and click **Generate**.

---## API Endpoints

| Method | Path            | Description                                      |

|--------|-----------------|--------------------------------------------------|

| `GET`  | `/api/styles`   | Returns the five available styles.               |

| `POST` | `/api/describe` | Accepts `file` + `style`, returns a description. |

---## Testing

pytest app/tests -v


```---## Cost & Rate-Limit Notes

- **Cost:** Only `POST /api/describe` calls the vision model and spends credits.

  Images are downscaled to `MAX_IMAGE_EDGE_PX` before being sent, reducing token

  usage. Use small test images while developing.

- **Rate limiting:** `/api/describe` is rate-limited per IP (via `slowapi`).

  Exceeding the limit returns `429`.

- **Size guard:** Requests larger than `MAX_FILE_SIZE_MB` are rejected early

  (before the full upload is buffered).

---## Configuration Reference

| Variable            | Default             | Description                               |

|---------------------|---------------------|-------------------------------------------|

| `GROQ_API_KEY`      | `None`              | Required only to generate descriptions.   |

| `GROQ_MODEL`        | `qwen/qwen3.6-27b`  | Groq vision model to use.                 |

| `MAX_FILE_SIZE_MB`  | `10`                | Maximum upload size.                      |

| `MAX_IMAGE_EDGE_PX` | `1536`              | Longest edge before downscaling kicks in. |