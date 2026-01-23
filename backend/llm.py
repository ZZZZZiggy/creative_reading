import json
import os
import re
from typing import List, Dict, Any
from schemas import DocumentResponse, Block, BlockAnnotations, BilingualAnchor, DocumentMeta


def extract_text_from_html(html: str) -> str:
    """从 HTML 中提取纯文本"""
    if not html:
        return ""
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_marker_children(children: List[Dict], blocks: List[Dict], block_counter: List[int]):
    """递归解析 marker 的 children 结构，提取文本块"""
    TEXT_TYPES = {"Text", "SectionHeader", "Title", "ListItem", "Caption", "Footnote"}

    for child in children:
        if not isinstance(child, dict):
            continue
        block_type = child.get("block_type", "")
        html = child.get("html", "")
        nested = child.get("children")

        if block_type in TEXT_TYPES and html:
            text = extract_text_from_html(html)
            if text and len(text) > 10:
                blocks.append({
                    "id": child.get("id", f"blk_{block_counter[0]:03d}"),
                    "type": "heading" if "Header" in block_type else "paragraph",
                    "content": text
                })
                block_counter[0] += 1

        if nested and isinstance(nested, list):
            parse_marker_children(nested, blocks, block_counter)


def get_llm_client():
    """
    Initialize and return Gemini LLM client
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY must be set in environment")

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        return genai, "gemini"
    except ImportError:
        raise ImportError("google-generativeai package is not installed. Install it with: pip install google-generativeai")


def get_system_prompt() -> str:
    """
    Generate a very detailed system prompt for AI document enrichment
    """
    return """You are an expert document analysis AI specialized in academic and technical document processing. Your task is to enrich raw document blocks extracted from PDFs with intelligent annotations that support two reading modes: Skim Mode and Intensive Reading Mode.

    ## Your Role
    You analyze document blocks (paragraphs, headings, etc.) and add structured annotations that help readers:
    1. **Skim Mode**: Quickly understand the main ideas through topic sentences and syntax structure
    2. **Intensive Mode**: Deeply understand technical terms through bilingual anchors and nuanced explanations

    ## Input Format
    You will receive JSON data containing document blocks from a PDF. Each block has:
    - `id`: unique block identifier
    - `type`: block type (paragraph, heading, table, etc.)
    - `content`: the text content of the block

    ## Output Format
    You must return a JSON object with enriched blocks. For each block, you should add an `annotations` object containing:

    ### 1. Topic Sentence Range (for Skim Mode)
    - **Field**: `topic_sentence_range`
    - **Type**: `[start_index, end_index]` (character positions in the content string)
    - **Purpose**: Identify the sentence that best summarizes the paragraph's main idea
    - **Rules**:
    - For paragraphs: Find the sentence that captures the core message
    - For headings: Usually the heading itself (range [0, heading_length])
    - For tables: Usually the caption or first row description
    - If no clear topic sentence exists, use the first sentence
    - Character indices are 0-based and inclusive of start, exclusive of end

    ### 2. SVO Structure (for Skim Mode - Advanced)
    - **Field**: `svo_structure`
    - **Type**: `{"subject": [start, end], "verb": [start, end], "object": [start, end]}`
    - **Purpose**: Identify Subject-Verb-Object structure in the topic sentence for syntax highlighting
    - **Rules**:
    - Extract from the topic sentence (identified in step 1)
    - `subject`: The main noun/noun phrase performing the action
    - `verb`: The main verb or verb phrase
    - `object`: The direct object or complement
    - Use character ranges relative to the topic sentence, NOT the entire block
    - If SVO structure is unclear (e.g., passive voice, complex sentences), you may omit this field
    - Keys must be exactly: "subject", "verb", "object"

    ### 3. Bilingual Anchors (for Intensive Mode)
    - **Field**: `bilingual_anchors`
    - **Type**: Array of objects with:
    - `term`: The technical term or jargon (string)
    - `range`: `[start_index, end_index]` in the block content (character positions)
    - `translation`: Translation in target language (default: Chinese if source is English, English if source is Chinese)
    - `nuance_note`: Detailed explanation of the term's meaning, context, and subtle differences
    - `trigger_threshold_ms`: Optional gaze duration in milliseconds (default: 800ms)
    - **Purpose**: Help readers understand technical terms by providing translations and explanations
    - **Rules**:
    - Identify 3-8 key technical terms, jargon, or domain-specific concepts per paragraph
    - Prioritize terms that are:
        * Central to understanding the paragraph
        * Likely unfamiliar to general readers
        * Domain-specific terminology
        * Acronyms or abbreviations (expand them)
    - For each term:
        * Find its exact position in the content string
        * Provide accurate translation
        * Write a nuanced explanation (2-3 sentences) covering:
        - Basic definition
        - Context-specific meaning
        - Why it matters in this document
        - Any subtle distinctions or common misconceptions
    - Character ranges are relative to the entire block content
    - Avoid over-annotating common words

    ## Processing Guidelines

    1. **Language Detection**:
    - Detect the source language automatically
    - If source is English, provide Chinese translations
    - If source is Chinese, provide English translations
    - If other languages, use English as default translation target

    2. **Block Type Handling**:
    - **Paragraphs**: Full annotation (topic sentence, SVO, bilingual anchors)
    - **Headings**: Usually only topic_sentence_range (the heading itself)
    - **Tables**: Focus on caption and first row, minimal annotations
    - **Code blocks**: Usually skip annotations
    - **Lists**: Annotate list items individually if substantial

    3. **Quality Standards**:
    - Topic sentences must be accurate and representative
    - SVO structure must be grammatically correct
    - Translations must be precise and contextually appropriate
    - Nuance notes must be informative but concise (2-3 sentences max)
    - Character ranges must be exact (verify by checking the content string)

    4. **Edge Cases**:
    - Very short blocks (< 50 chars): Minimal annotations
    - Very long blocks (> 2000 chars): Focus on first few paragraphs
    - Mathematical formulas: Skip or provide conceptual explanation
    - Citations: Usually skip annotations

    ## Output JSON Structure
    Return a JSON object with this structure:
    ```json
    {
    "blocks": [
        {
        "id": "original_block_id",
        "type": "original_type",
        "content": "original_content",
        "annotations": {
            "topic_sentence_range": [start, end],
            "svo_structure": {
            "subject": [start, end],
            "verb": [start, end],
            "object": [start, end]
            },
            "bilingual_anchors": [
            {
                "term": "technical_term",
                "range": [start, end],
                "translation": "翻译",
                "nuance_note": "Detailed explanation...",
                "trigger_threshold_ms": 800
            }
            ]
        }
        }
    ]
    }
    ```

    ## Important Notes
    - All character indices are 0-based
    - Ranges are [start, end) - start inclusive, end exclusive
    - Preserve all original block fields (id, type, content)
    - Only add annotations where meaningful
    - If a field cannot be determined, omit it (don't use null)
    - Be precise with character positions - verify them against the content string
    - Maintain consistency in translation language throughout the document

    ## Example
    Input block:
    ```json
    {
    "id": "blk_01",
    "type": "paragraph",
    "content": "Quantum entanglement is a physical phenomenon that occurs when pairs of particles become correlated."
    }
    ```

    Output:
    ```json
    {
    "id": "blk_01",
    "type": "paragraph",
    "content": "Quantum entanglement is a physical phenomenon that occurs when pairs of particles become correlated.",
    "annotations": {
        "topic_sentence_range": [0, 105],
        "svo_structure": {
        "subject": [0, 22],
        "verb": [23, 26],
        "object": [27, 105]
        },
        "bilingual_anchors": [
        {
            "term": "Quantum entanglement",
            "range": [0, 22],
            "translation": "量子纠缠",
            "nuance_note": "A fundamental concept in quantum mechanics where two or more particles become linked in such a way that the quantum state of each particle cannot be described independently, even when separated by large distances. Einstein famously called this 'spooky action at a distance'.",
            "trigger_threshold_ms": 800
        },
        {
            "term": "correlated",
            "range": [88, 98],
            "translation": "关联",
            "nuance_note": "In quantum mechanics, correlation means the particles' properties are interdependent, such that measuring one particle instantly affects the other, regardless of distance.",
            "trigger_threshold_ms": 800
        }
        ]
    }
    }
    ```

    Now process the input blocks and return the enriched JSON structure."""


def call_llm_for_enrichment(blocks: List[Dict[str, Any]], client, client_type: str) -> Dict[str, Any]:
    """
    Call LLM to enrich document blocks with annotations
    """
    system_prompt = get_system_prompt()

    # Prepare input blocks (simplified structure for LLM)
    input_blocks = [
        {
            "id": block.get("id", f"blk_{i}"),
            "type": block.get("type", "paragraph"),
            "content": block.get("content", "")
        }
        for i, block in enumerate(blocks)
    ]

    user_prompt = f"""Please analyze and enrich the following document blocks with annotations.

Input blocks:
{json.dumps(input_blocks, ensure_ascii=False, indent=2)}

Return the enriched blocks in the exact JSON format specified in the system prompt."""

    try:
        if client_type == "gemini":
            # Combine system prompt and user prompt for Gemini
            # Gemini doesn't have a separate system message, so we combine them
            full_prompt = f"""{system_prompt}

{user_prompt}

IMPORTANT: You must return ONLY valid JSON in the exact format specified above. Do not include any markdown code blocks, explanations, or additional text outside the JSON."""

            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            model = client.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.3,
                    "response_mime_type": "application/json",
                }
            )

            response = model.generate_content(full_prompt)
            result = json.loads(response.text)
        else:
            raise ValueError(f"Unknown client type: {client_type}")

        return result
    except Exception as e:
        print(f"[LLM] Error during enrichment: {e}")
        raise


def enrich_with_llm(data: dict, doc_id: str, title: str) -> DocumentResponse:
    """
    Enrich marker output data with LLM-generated annotations

    Args:
        data: Raw marker output JSON data
        doc_id: Document ID
        title: Document title

    Returns:
        DocumentResponse with enriched blocks
    """
    # Extract blocks from marker output
    # Marker output structure may vary, try common patterns
    blocks = []

    if isinstance(data, dict):
        # Try different possible structures
        if "children" in data and isinstance(data["children"], list):
            # Marker tree structure - recursively parse children
            block_counter = [0]
            parse_marker_children(data["children"], blocks, block_counter)
        elif "blocks" in data:
            blocks = data["blocks"]
        elif "pages" in data:
            # Flatten pages into blocks
            for page in data["pages"]:
                if "blocks" in page:
                    blocks.extend(page["blocks"])
        elif "content" in data:
            # Single content block
            blocks = [data["content"]] if isinstance(data["content"], dict) else data.get("blocks", [])
        else:
            # Assume the dict itself contains block-like structure
            blocks = [data] if "content" in data or "text" in data else []
    elif isinstance(data, list):
        blocks = data

    if not blocks:
        print("[LLM] Warning: No blocks found in marker output, creating minimal structure")
        # Create a minimal block from the entire content
        content = json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else data
        blocks = [{"id": "blk_01", "type": "paragraph", "content": content[:1000]}]

    # Normalize block structure
    normalized_blocks = []
    for i, block in enumerate(blocks):
        if isinstance(block, dict):
            normalized_blocks.append({
                "id": block.get("id", f"blk_{i:03d}"),
                "type": block.get("type", block.get("block_type", "paragraph")),
                "content": block.get("content", block.get("text", block.get("markdown", "")))
            })
        elif isinstance(block, str):
            normalized_blocks.append({
                "id": f"blk_{i:03d}",
                "type": "paragraph",
                "content": block
            })

    # Call LLM for enrichment
    try:
        client, client_type = get_llm_client()
        print(f"[LLM] Enriching {len(normalized_blocks)} blocks using {client_type}...")

        # Process in batches if too many blocks (to avoid token limits)
        batch_size = 10
        enriched_blocks = []

        for i in range(0, len(normalized_blocks), batch_size):
            batch = normalized_blocks[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(normalized_blocks) + batch_size - 1) // batch_size
            print(f"[LLM] Processing batch {batch_num}/{total_batches}...")

            try:
                batch_result = call_llm_for_enrichment(batch, client, client_type)
                enriched_blocks.extend(batch_result.get("blocks", []))
            except Exception as batch_error:
                print(f"[LLM] Batch {batch_num} failed: {batch_error}, using original blocks without annotations")
                # Use original blocks without annotations for this batch
                enriched_blocks.extend(batch)

        # Convert enriched blocks to Pydantic models
        pydantic_blocks = []
        for block_data in enriched_blocks:
            annotations_data = block_data.get("annotations")
            annotations = None

            if annotations_data:
                # Parse bilingual anchors
                bilingual_anchors = None
                if annotations_data.get("bilingual_anchors"):
                    bilingual_anchors = [
                        BilingualAnchor(**anchor) for anchor in annotations_data["bilingual_anchors"]
                    ]

                # Parse SVO structure (convert list to dict if needed)
                svo_structure = annotations_data.get("svo_structure")
                if svo_structure and isinstance(svo_structure, list):
                    # Convert old format [[0,18], [19,21], [22,42]] to dict
                    if len(svo_structure) == 3:
                        svo_structure = {
                            "subject": tuple(svo_structure[0]),
                            "verb": tuple(svo_structure[1]),
                            "object": tuple(svo_structure[2])
                        }
                    else:
                        svo_structure = None
                elif svo_structure and isinstance(svo_structure, dict):
                    # Ensure tuples
                    svo_structure = {k: tuple(v) if isinstance(v, list) else v
                                   for k, v in svo_structure.items()}

                annotations = BlockAnnotations(
                    topic_sentence_range=tuple(annotations_data["topic_sentence_range"])
                        if annotations_data.get("topic_sentence_range") else None,
                    svo_structure=svo_structure,
                    bilingual_anchors=bilingual_anchors
                )

            pydantic_blocks.append(Block(
                id=block_data.get("id", "unknown"),
                type=block_data.get("type", "paragraph"),
                content=block_data.get("content", ""),
                annotations=annotations
            ))

        # Extract metadata if available
        meta = None
        if isinstance(data, dict):
            if "meta" in data or "metadata" in data:
                meta_data = data.get("meta") or data.get("metadata", {})
                meta = DocumentMeta(
                    difficulty=meta_data.get("difficulty"),
                    domain=meta_data.get("domain"),
                    language=meta_data.get("language", "en-US")
                )

        return DocumentResponse(
            doc_id=doc_id,
            title=title,
            meta=meta,
            blocks=pydantic_blocks
        )

    except Exception as e:
        print(f"[LLM] Error during enrichment, falling back to basic structure: {e}")
        # Fallback: return basic structure without LLM enrichment
        pydantic_blocks = [
            Block(
                id=block.get("id", f"blk_{i:03d}"),
                type=block.get("type", "paragraph"),
                content=block.get("content", "")
            )
            for i, block in enumerate(normalized_blocks)
        ]

        return DocumentResponse(
            doc_id=doc_id,
            title=title,
            blocks=pydantic_blocks
        )
