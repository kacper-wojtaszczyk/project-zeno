# 🌳 Project Zeno: Narrative Experiments Fork

**Upstream Project:** [wri/project-zeno](https://github.com/wri/project-zeno) — Global Nature Watch Agent  
**This Fork's Focus:** Transforming forest data into emotional, aesthetic, and experimental narratives

---

## 🎭 What This Fork Does

While the upstream project provides factual, comprehensive forest monitoring narratives, **this fork explores the creative, emotional, and aesthetic dimensions of deforestation data**.

We're building experimental narrative tools that transform WRI/GFW forest change data into alternative formats:

- 🖊️ **Haiku & Micro-poetry** — Ultra-constrained literary formats (5-7-5 syllables) that distill forest loss into emotional resonance
- 🎵 **Soundscapes** — Audio representations of forests and their silence
- 📖 **Speculative Fiction** — "What if" narratives, counterfactual stories, climate fiction
- 🌍 **Parallel Earths** — Visualizations of alternate timelines with different conservation choices
- 🎨 **Visual Narratives** — Artistic interpretations of data (stretch goal)

**Why?** Because sometimes the most powerful way to communicate about environmental change isn't through charts and statistics—it's through haiku about silence, soundscapes of loss, or stories about forests that might have been.

**This is a learning project:** Understanding production LangGraph agent architecture while experimenting with narrative generation for conservation tech.

---

## 📖 About the Upstream Project

The core of the upstream project is an LLM-powered agent that drives conversations for Global Nature Watch. It's a production-quality ReAct agent implemented in LangGraph that:

- Retrieves areas of interest
- Selects appropriate datasets via RAG
- Retrieves statistics from the WRI analytics API
- Generates factual insights including charts from the data

We respect and preserve this architecture—our narrative tools extend it, not replace it.

For detailed technical architecture, see [Agent Architecture Documentation](docs/AGENT_ARCHITECTURE.md).

---

## 🎨 Narrative Tools Extension (This Fork)

Our additions follow a modular pattern that respects the upstream architecture:

```
User Query → API → Agent → Tools → [NEW: Narrative Tools] → Creative Output Formats
```

**Extension Points:**
- `/src/narrative_tools/` — Experimental narrative generators (haiku, soundscapes, fiction)
- `/src/agent/tools/narrative_*.py` — Agent tool wrappers for narrative capabilities
- `/tests/narrative_tools/` — Tests for our additions
- `/docs/narrative_tools/` — Documentation for experimental formats

**Philosophy:** Keep the core unchanged. Add experimental tools as isolated, reusable modules that could potentially be contributed upstream if they prove valuable.

**Current Status:** Foundation phase—studying upstream patterns before implementing narrative generators.

---

## Dependencies

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [postgresql](https://www.postgresql.org/) (for using local DB instead of docker)
- [docker](https://docs.docker.com/)

## Local Development Setup

We use uv for package management and docker-compose
for running the sytem locally.

1. **Clone and setup:**

   ```bash
   # Clone this fork (or your own fork of this narrative experiments fork)
   git clone git@github.com:kacperwojtas/project-zeno.git
   cd project-zeno
   uv sync
   source .venv/bin/activate
   ```

2. **Environment configuration:**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys and credentials

   cp .env.local.example .env.local
   # .env.local contains local development overrides (auto-created by make commands)
   ```

3. **Build dataset RAG database:**

   Our agent uses a RAG database to select datasets. The RAG database
   can be built locally using

   ```bash
   uv run python src/ingest/embed_datasets.py
   ```

   As an alternative ,the current production table can also be
   retrieved from S3 if you have the corresponding access permissions.

   ```bash
   aws s3 sync s3://zeno-static-data/ data/
   ```

4. **Start infrastructure services:**

   ```bash
   make up       # Start Docker services (PostgreSQL + Langfuse + ClickHouse)
   ```

5. **Ingest data (required after starting database):**

   After starting the database and infrastructure services, you need to ingest the required datasets. Feel free to run all or just the ones you need.

   This downloads ~2 GB of data per dataset except for WDPA which is ~10 GB. It's ok to skip WDPA if you don't need it.

   Make sure you're set up with WRI AWS credentials in your `.env` file to access the S3 bucket.

   ```bash
   python src/ingest/ingest_gadm.py
   python src/ingest/ingest_kba.py
   python src/ingest/ingest_landmark.py
   python src/ingest/ingest_wdpa.py
   ```

   See `src/ingest/` directory for details on each ingestion script.

6. **Start application services:**

   ```bash
   make api      # Run API locally (port 8000)
   make frontend # Run Streamlit frontend (port 8501)
   ```

   Or start everything at once (after data ingestion):

   ```bash
   make dev      # Starts API + frontend (requires infrastructure already running)
   ```

7. **Setup Local Langfuse:**
   a. Clone the Langfuse repository outside your current project directory

   ```bash
   cd ..
   git clone https://github.com/langfuse/langfuse.git
   cd langfuse
   ```

   b. Start the Langfuse server

   ```bash
   docker compose up -d
   ```

   c. Access the Langfuse UI at <http://localhost:3000>
   1. Create an account
   2. Create a new project
   3. Copy the API keys from your project settings

   d. Return to your project directory and update your .env.local file

   ```bash
   cd ../project-zeno
   # Update these values in your .env.local file:
   LANGFUSE_HOST=http://localhost:3000
   LANGFUSE_PUBLIC_KEY=your_public_key_here
   LANGFUSE_SECRET_KEY=your_secret_key_here
   ```

8. **Access the application:**

   - Frontend: <http://localhost:8501>
   - API: <http://localhost:8000>
   - Langfuse: <http://localhost:3000>

## Development Commands

```bash
make help     # Show all available commands
make up       # Start Docker infrastructure
make down     # Stop Docker infrastructure
make api      # Run API with hot reload
make frontend # Run frontend with hot reload
make dev      # Start full development environment
```

## Testing

### API Tests

Running `make up` will bring up a `zeno-db_test` database that's used by pytest. The tests look for a `TEST_DATABASE_URL` environment variable (also set in .env.local). You can also create the database manually with the following commands:

```bash
createuser -s postgres # if you don't have a postgres user
createdb -U postgres zeno-data_test
```

Then run the API tests using pytest:

```bash
uv run pytest tests/api/
```

## CLI User Management

For user administration commands (making users admin, whitelisting emails), see [CLI Documentation](docs/CLI.md).

## Environment Files

- `.env` - Base configuration (production settings)
- `.env.local` - Local development overrides (auto-created)

The system automatically loads `.env` first, then overrides with `.env.local` for local development.

```bash
uv run streamlit run src/frontend/app.py
```

## Setup Database

1. Using docker:

   ```bash
   docker compose up -d
   uv run streamlit run frontend/app.py
   ```

2. Using postgresql:

   a. Create a new database

   ```bash
   createuser -s postgres # if you don't have a postgres user
   createdb -U postgres zeno-data-local
   alembic upgrade head

   # Check if you have the database running
   psql zeno-data-local

   # Check if you have the tables created
   \dt

   # Output
   #               List of relations
   #  Schema |      Name       | Type  |  Owner
   # --------+-----------------+-------+----------
   #  public | alembic_version | table | postgres
   #  public | threads         | table | postgres
   #  public | users           | table | postgres
   ```

   b. Add the database URL to the .env file:

   ```bash
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/zeno-data-local
   ```

## Configure localhost Langfuse

1. `docker compose up langfuse-server` (or just spin up the whole backend with `docker compose up`)
2. Open your browser and navigate to <http://localhost:3000> to create a Langfuse account.
3. Within the Langfuse UI, create an organization and then a project.
4. Copy the API keys (public and secret) generated for your project.
5. Update the `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` environment variables in your `docker-compose.yml` file with the copied keys.

## Dataset lookup RAG

After syncing the data, use the latest version of the zeno data clean csv file to
create embeddings that are used for looking up datasets based on queries.

The latest csv reference file currently is

```bash
aws s3 cp s3://zeno-static-data/zeno_data_clean_v2.csv data/
```

then run

```bash
python src/ingest/embed_datasets.py
```

This will update the local database at `data/zeno-docs-openai-index`.

---

## 🤝 Fork Relationship & Contributing

**Upstream Sync:** This fork periodically syncs with [wri/project-zeno](https://github.com/wri/project-zeno) to stay current with improvements to the core agent architecture.

**Contribution Philosophy:**
- **To this fork:** Experiments with narrative formats, creative data storytelling, aesthetic interpretations of forest data
- **To upstream:** If narrative tools prove valuable and align with upstream goals, we may propose contributions

**Not accepting:** Changes that modify core agent behavior or upstream functionality—those belong in the upstream project.

**Contact:** Open a github issue!

**License:** MIT (inherited from upstream)

