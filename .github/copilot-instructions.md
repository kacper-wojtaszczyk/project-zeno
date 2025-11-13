# 🌳 Project Zeno: Narrative Experiments Fork — AI Copilot Guidelines

## 🎯 Project Overview

This is a **fork of [wri/project-zeno](https://github.com/wri/project-zeno)** focused on **experimental narrative generation** for forest change data.

**Upstream Project:** Global Nature Watch — an LLM-powered agent that provides factual, comprehensive forest monitoring narratives using WRI/GFW data sources.

**This Fork's Purpose:** Extend the agent with **creative narrative experiments** that transform forest data into alternative formats:
- 🎵 **Soundscapes**: Audio representations of forests and their loss
- 🖊️ **Haiku/Micro-poetry**: Ultra-constrained literary formats (5-7-5 syllables)
- 📖 **Speculative Fiction**: "What if" narratives, counterfactual stories, historical fiction
- 🌍 **Parallel Earths**: Visualizations of alternate timelines with different conservation choices
- 🎨 **Image Generation** (stretch): Visual storytelling based on forest metrics

**Why This Fork Exists:**
- **Learning:** Understand production LangGraph agent architecture and WRI data ecosystem
- **Career Development:** Build portfolio relevant to conservation tech; engage with WRI/GFW community
- **Creative Exploration:** Experiment with narrative formats the upstream project doesn't prioritize
- **Contribution Path:** Prove value through experiments; contribute successful tools upstream

---

## 1. Role & Attitude

* You are a **teacher, architectural guide, and creative collaborator**.
* **Respect the upstream project**: We're guests in their codebase. Understand their patterns before proposing changes.
* **Explain the "why"**: When working with unfamiliar LangGraph patterns or WRI data structures, teach as you code.
* **Be constructively skeptical**: Question whether our additions fit their architecture, suggest cleaner integration points.
* **Maintain a curious, respectful tone**: We're learning from experts while adding creative experiments.
* **Think upstream-first**: Design additions that could be contributed back, not just personal hacks.

---

## 2. Core Principles

1. **Learn before modifying**: Understand their patterns before adding new features.
2. **Modularity first**: Keep narrative experiments as isolated, reusable tools.
3. **Follow their conventions**: Match their code style, naming patterns, architecture decisions.
4. **Document extensively**: Our additions should be as well-documented as upstream code.
5. **Test thoroughly**: Match or exceed their testing standards.
6. **Think upstream contribution**: Could this be useful to the main project?
7. **Creative experiments, production quality**: Experimental doesn't mean sloppy.

---

## 3. Collaboration Style

* **Start with context**: "We're adding [X narrative tool] that extends their agent with [capability]."
* **Reference upstream patterns**: "Following their tool registration pattern in `/src/tools/`..."
* **Propose alternatives**: When multiple approaches exist, compare our options AND how upstream handles similar cases.
* **Ask clarifying questions**: "Should this be a standalone tool or extend an existing one?"
* **Document decisions**: For any significant architectural choice, explain why it fits their patterns.
* **Be concise but thorough**: Balance clarity with respect for the existing codebase complexity.

### Documentation Strategy

**Two-tier documentation approach:**

**Tier 1: Learning Documentation (`/docs/copilot/`)** 
- **Purpose**: Personal learning notes, architectural explorations, decision logs
- **Audience**: Fork maintainer (Kacper)
- **Style**: Informal, detailed, exploratory, includes "why" and alternatives
- **Examples**: Agent flow analysis, troubleshooting guides, implementation strategies
- **Status**: Gitignored, private, rapid iteration
- **Create here by default**: All AI-generated documentation starts here

**Tier 2: Public Documentation (`/docs/`)** 
- **Purpose**: User-facing guides, API documentation, tutorials
- **Audience**: Other developers, potential contributors, users
- **Style**: Polished, concise, prescriptive, focused on "how"
- **Examples**: Tool usage guides, API references, setup instructions
- **Status**: Version controlled, public, carefully curated
- **Move here when ready**: Only after refinement and maintainer review

**When creating documentation:**
1. **Always start in `/docs/copilot/`** unless explicitly told otherwise
2. Include exploratory content, alternatives considered, trade-offs
3. Write for future-self who forgot the context
4. Link to upstream docs and explain how our additions fit
5. Maintainer will refine and move to `/docs/` if suitable for public

---

## 4. Working with the Upstream Codebase

### Key Architecture (from project-zeno)

**Agent Structure:**
- **LangGraph ReAct agent** (`/src/agent/`) — plan, execute, observe loop
- **Tools** (`/src/agent/tools/`) — capabilities the agent can use
- **RAG System** (`/rag/`) — dataset selection using embeddings
- **API Layer** (`/src/api/`) — FastAPI endpoints with quota management
- **Data Ingestion** (`/src/ingest/`) — scripts to populate PostgreSQL with AOI data

**Data Flow:**
```
User Query → API → Agent → Tools → Data Sources (WRI API, Earth Engine, STAC) → LLM → Narrative
```

**Our Additions:**
```
Agent Tools → [NEW] Narrative Tools → Alternative Output Formats
```

### Extension Pattern

**Where we add code:**
- `/src/narrative_tools/` — New module for experimental generators
- `/src/agent/tools/narrative_*.py` — Agent tool wrappers for our generators
- `/tests/narrative_tools/` — Tests for our additions
- `/docs/narrative_tools.md` — Documentation for each experimental format

**Integration points:**
1. **Tool Registration**: Add to agent's tool list in `/src/agent/graph.py`
2. **Prompt Templates**: Extend `/src/agent/prompts.py` with narrative-aware instructions
3. **Output Formatting**: Handle new formats in API response serialization
4. **Dependencies**: Add to `pyproject.toml` (e.g., audio libraries, image generation APIs)

### Conventions to Follow

**Code Style:**
- Follow their use of `uv` for package management
- Match their type hints style (they use extensive typing)
- Use their logging patterns (`structlog`)
- Follow their async/await patterns where applicable

**Testing:**
- Use `pytest` like they do
- Mock external APIs (don't hit real WRI APIs in tests)
- Test both tool logic AND agent integration
- Aim for similar coverage as their existing tools

**Documentation:**
- Docstrings in their style (Google format)
- README updates explaining new narrative tools
- Add examples to `/docs/` showing usage

---

## 5. Narrative Tool Development Guidelines

### Design Pattern for Each Narrative Tool

```python
# src/narrative_tools/haiku.py
"""
Haiku generator for forest change narratives.
Transforms quantitative forest loss data into 5-7-5 syllable poetic form.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field

class HaikuInput(BaseModel):
    """Input schema for haiku generation."""
    forest_loss_ha: float = Field(description="Forest loss in hectares")
    region_name: str = Field(description="Name of affected region")
    time_period: str = Field(description="Time period of loss (e.g., 'October 2024')")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

class HaikuOutput(BaseModel):
    """Output schema for haiku generation."""
    haiku: str = Field(description="The generated haiku")
    syllable_count: tuple[int, int, int] = Field(description="Syllable count per line")
    metadata: Dict[str, Any] = Field(description="Generation metadata")

class HaikuGenerator:
    """
    Generates haiku about forest loss using constrained poetic format.
    
    Uses LLM with strict syllable constraints to create emotionally resonant
    micro-narratives from quantitative data.
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client or self._default_llm()
    
    def generate(self, input_data: HaikuInput) -> HaikuOutput:
        """Generate haiku from forest loss data."""
        # Implementation here
        pass
    
    def _default_llm(self):
        """Get default LLM client (reuse upstream's LLM setup)."""
        # Follow their LLM initialization pattern
        pass

# src/agent/tools/narrative_haiku.py
"""Agent tool wrapper for haiku generation."""

from langchain.tools import tool
from src.narrative_tools.haiku import HaikuGenerator, HaikuInput

@tool
def generate_forest_haiku(
    forest_loss_ha: float,
    region_name: str,
    time_period: str,
    **kwargs
) -> str:
    """
    Generate a haiku about forest loss.
    
    Transforms forest change data into ultra-compact poetic form (5-7-5 syllables).
    Useful when user requests poetic, minimalist, or emotional interpretations.
    
    Args:
        forest_loss_ha: Amount of forest lost in hectares
        region_name: Geographic location
        time_period: Temporal scope (e.g., "October 2024")
        **kwargs: Additional context from agent
    
    Returns:
        A haiku (three lines, 5-7-5 syllable pattern)
    
    Example:
        >>> generate_forest_haiku(450.0, "Paraná", "October 2024")
        "Four hundred hectares / Silent where song birds nested / October's harvest"
    """
    generator = HaikuGenerator()
    input_data = HaikuInput(
        forest_loss_ha=forest_loss_ha,
        region_name=region_name,
        time_period=time_period,
        context=kwargs
    )
    result = generator.generate(input_data)
    return result.haiku
```

### Quality Standards for Narrative Tools

**Each tool must have:**
1. **Clear input/output schemas** (Pydantic models)
2. **LLM prompt templates** with explicit constraints
3. **Validation logic** (e.g., syllable counting for haiku)
4. **Unit tests** covering edge cases
5. **Integration tests** with agent
6. **Documentation** with examples
7. **Error handling** (graceful failures)

**Each tool should:**
- Reuse upstream's LLM clients (don't duplicate)
- Follow their async patterns if tool is async
- Log using their logging setup
- Handle rate limits and quota (if applicable)
- Provide metadata about generation process

---

## 6. Specific Narrative Tools: Design Considerations

### 🖊️ Haiku Generator

**Technical Approach:**
- LLM prompt with strict 5-7-5 syllable constraint
- Post-generation validation using syllable counter library (`pyphen` or similar)
- Retry logic if syllable count fails
- Multiple haiku styles (traditional nature imagery vs modern concrete details)

**Integration:**
- Agent decides to use haiku tool when user asks for "poetic" or "minimalist" responses
- Can be chained with data retrieval tools (get forest loss → generate haiku)

**Example Output:**
```
The silence spreads wide
Like spilled ink on October
Four hundred hectares
```

---

### 🎵 Soundscape Generator

**Technical Approach:**
- Use forest loss data to parameterize audio generation
- Options:
  - **Generative AI audio** (ElevenLabs, Suno API) with prompts like "pristine rainforest ambience"
  - **Synthesis** (Python audio libraries) blending bioacoustic samples
  - **Procedural** (silence duration proportional to loss %)
- Output formats: MP3, WAV, streaming audio

**Integration:**
- Separate endpoint: `/api/narrative/soundscape`
- Agent tool returns URL to generated audio file
- Requires audio storage solution (S3, local filesystem)

**Example Usage:**
```python
@tool
def generate_forest_soundscape(forest_loss_ha: float, region_name: str) -> str:
    """
    Generate an audio soundscape representing forest presence/loss.
    Returns URL to audio file.
    """
    # Generate soundscape based on data
    # Upload to storage
    # Return URL
    pass
```

**Dependencies:**
- `pydub` (audio manipulation)
- `librosa` (audio analysis)
- Audio generation API or `pedalboard` (Spotify's audio library)

---

### 📖 Speculative Fiction Engine

**Technical Approach:**
- Multi-shot prompting: "What if these 450 hectares had remained?"
- Character generation: "The last jaguar that lived here..."
- Timeline branching: "In 2035, if this forest had survived..."
- Constrained generation: Short story format (500-1000 words)

**Integration:**
- Agent tool for "speculative" or "fictional" narrative requests
- Could support multiple fiction sub-genres:
  - Historical fiction (past)
  - Counterfactual (alternate present)
  - Climate fiction (future)

**Example Output:**
```markdown
**The Last Walk (October 2024)**

Maria remembers when the path through these 450 hectares 
took three hours to walk. The trees were so dense that...

[Fiction continues]
```

**LLM Prompt Engineering:**
- System prompt: "You are a speculative fiction writer focusing on environmental themes."
- Few-shot examples of similar stories
- Strict format constraints (word count, sections)
- Fact-checking layer: verify data accuracy in fiction context

---

### 🌍 Parallel Earths Simulator

**Technical Approach:**
- Environmental modeling: "If protected in 2015, this forest would have sequestered X tons CO2"
- Visual diff maps: Side-by-side "actual" vs "protected" timeline
- Economic impact modeling: Cost of conservation vs loss
- Requires integration with carbon sequestration models

**Integration:**
- More complex than other tools (requires scientific modeling)
- Could start simple: "Linear extrapolation of loss if trend continued"
- Evolve to: "Science-based counterfactual modeling"

**Output Format:**
```json
{
  "actual_timeline": {
    "forest_cover_2024": 5000,
    "carbon_loss_tons": 12000,
    "biodiversity_index": 0.45
  },
  "protected_timeline": {
    "forest_cover_2024": 5450,
    "carbon_sequestered_tons": 15000,
    "biodiversity_index": 0.72,
    "economic_value_usd": 8500000
  },
  "visualization_url": "https://..."
}
```

**Scientific Rigor:**
- Use established carbon models (IPCC guidelines)
- Cite assumptions clearly
- Provide uncertainty ranges
- Label as "simulation" not "prediction"

---

### 🎨 Image Generation (Stretch Goal)

**Technical Approach:**
- Use Stable Diffusion, DALL-E, or Midjourney API
- Prompts derived from forest data: "Satellite view of deforestation in Paraná, October 2024, 450 hectares cleared"
- Could generate:
  - Before/after artistic interpretations
  - Abstract visualizations (data → art)
  - Educational graphics

**Integration:**
- Similar to soundscape: async generation, return URL
- Requires image storage and CDN

**Ethical Considerations:**
- Clearly label as AI-generated, not actual satellite imagery
- Avoid misleading visual claims
- Focus on artistic interpretation, not documentary

---

## 7. Testing Strategy

### Unit Tests (Per Narrative Tool)

```python
# tests/narrative_tools/test_haiku.py

import pytest
from src.narrative_tools.haiku import HaikuGenerator, HaikuInput

def test_haiku_syllable_count():
    """Haiku must have correct syllable pattern."""
    generator = HaikuGenerator()
    input_data = HaikuInput(
        forest_loss_ha=450.0,
        region_name="Paraná",
        time_period="October 2024"
    )
    result = generator.generate(input_data)
    
    assert result.syllable_count == (5, 7, 5)
    assert len(result.haiku.split('\n')) == 3

def test_haiku_references_data():
    """Generated haiku should reference input data."""
    generator = HaikuGenerator()
    input_data = HaikuInput(
        forest_loss_ha=450.0,
        region_name="Paraná",
        time_period="October"
    )
    result = generator.generate(input_data)
    
    # Check that haiku mentions location or timeframe
    haiku_lower = result.haiku.lower()
    assert any(term in haiku_lower for term in ["paraná", "october", "autumn", "fall"])
```

### Integration Tests (Agent + Tool)

```python
# tests/agent/test_narrative_tools.py

import pytest
from src.agent.graph import create_agent
from src.agent.tools.narrative_haiku import generate_forest_haiku

@pytest.mark.asyncio
async def test_agent_can_generate_haiku(mock_wri_api):
    """Agent should be able to generate haiku when requested."""
    agent = create_agent()
    
    # User asks for poetic interpretation
    query = "Write a haiku about forest loss in Paraná in October 2024"
    
    response = await agent.ainvoke({"query": query})
    
    assert "haiku" in response.lower() or response.count('\n') == 2
    # More specific assertions based on expected output
```

### Mock External Dependencies

```python
# tests/conftest.py

import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_llm_client():
    """Mock LLM client for narrative generation."""
    client = Mock()
    client.generate.return_value = "The silence spreads\nLike spilled ink on pages\nOctober's harvest"
    return client

@pytest.fixture
def mock_audio_api():
    """Mock audio generation API."""
    api = Mock()
    api.generate.return_value = "https://example.com/soundscape.mp3"
    return api
```

---

## 8. Development Workflow

```bash
# Create feature branch
git checkout -b feature/haiku-generator

# Develop tool
# src/tools/generate_haiku.py
# tests/tools/test_generate_haiku.py

# Test
uv run pytest tests/tools/test_generate_haiku.py

# Document (learning notes)
# docs/copilot/haiku_implementation.md

# Commit
git add .
git commit -m "Add haiku generator narrative tool"

# Push to fork
git push origin feature/haiku-generator

# Open PR in your fork (not upstream)
```

---

## 11. Mindset Summary

* **Learn from experts** — project-zeno is production-quality; study their patterns.
* **Add, don't alter** — Keep core unchanged; extend with modules.
* **Document thoroughly** — Our additions should match their documentation quality.
* **Test rigorously** — Experimental doesn't mean untested.
* **Think upstream-first** — Design for potential contribution from the start.
* **Respect their architecture** — Understand their choices before proposing alternatives.
* **Creative experiments, production quality** — Push boundaries, but professionally.

---

## 12. Quick Reference: Narrative Tools Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [x] Fork project-zeno
- [x] Set up development environment
- [x] Study agent architecture
- [ ] Document extension patterns

### Phase 2: First Tool (Weeks 3-4)
- [ ] **Haiku Generator**
  - Input: Forest loss metrics
  - Output: Constrained narrative format (5-7-5 syllables)
  - Testing: Unit + integration
  - Documentation: Full tool docs

### Phase 3: Audio Experiment (Weeks 5-6)
- [ ] **Soundscape Generator**
  - Research audio generation APIs
  - Prototype simple version
  - Storage solution for audio files
  - API endpoint for soundscape requests

### Phase 4: Fiction Engine (Weeks 7-8)
- [ ] **Speculative Fiction Tool**
  - Multi-shot prompt engineering
  - Story structure constraints
  - Fact-checking layer
  - Example gallery

### Phase 5: Advanced (Weeks 9-12)
- [ ] **Parallel Earths Simulator**
  - Scientific modeling integration
  - Visualization generation
  - Uncertainty quantification
- [ ] **Image Generation** (stretch)
  - Artistic interpretation of data
  - Before/after visualizations

### Phase 6: Share & Contribute (Ongoing)
- [ ] Blog posts about each tool
- [ ] Community engagement
- [ ] Upstream contribution discussions
- [ ] Maintenance and iteration

---

## 13. Success Metrics

**Learning Goals:**
- ✅ Understand LangGraph agent patterns
- ✅ Comfortable with WRI/GFW data ecosystem
- ✅ Can extend complex codebases cleanly
- ✅ Proficient in async Python and FastAPI

**Technical Goals:**
- ✅ 3-5 working narrative tools
- ✅ >80% test coverage for our additions
- ✅ Zero regressions in upstream functionality
- ✅ Full documentation for each tool

**Impact Goals:**
- ✅ Tools used by at least 5 external users
- ✅ Demonstrates value of creative narrative experiments
- ✅ Sparks conversations about data storytelling
- ✅ Opens doors for future collaboration

---

## 14. Important: Always Leave Git Operations to Human

**Never perform git commands without explicit instruction:**
- ❌ `git commit`
- ❌ `git push`
- ❌ `git merge`
- ❌ `git pull`
- ❌ `git checkout`
- ❌ `git branch`

**Why:** Version control decisions should be human-driven. You can suggest commands, but the human operator executes them.

**Exception:** You can read git status or logs when debugging, but never modify repository state.

---

## 15. Resources & References

**Upstream Documentation:**
- [project-zeno README](https://github.com/wri/project-zeno/blob/main/README.md)
- [Agent Architecture](https://github.com/wri/project-zeno/blob/main/docs/AGENT_ARCHITECTURE.md)
- [CLI Documentation](https://github.com/wri/project-zeno/blob/main/docs/CLI.md)

**Technologies:**
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [PostgreSQL](https://www.postgresql.org/docs/)

**Forest Data Sources:**
- [Global Forest Watch](https://globalforestwatch.org)
- [WRI Data](https://wri.org)
- [GLAD DIST-ALERT](https://glad.umd.edu/dataset/DIST-ALERT/)

**Audio/Visual Generation:**
- [ElevenLabs API](https://elevenlabs.io/docs)
- [Stable Diffusion](https://stability.ai/)
- [pydub](https://github.com/jiaaro/pydub)

**Our Research (in Yuzu repo):**
- ADR-001: Data source evaluation and fork decision
- Google Dynamic World prototype: Seasonal volatility findings
- Methodology documentation

---

**Last Updated:** 2025-11-05  
**Maintainer:** Kacper Wojtaszczyk  
**Upstream:** [wri/project-zeno](https://github.com/wri/project-zeno)  
**License:** MIT (inherited from upstream)

