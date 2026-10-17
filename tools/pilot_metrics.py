from __future__ import annotations

import math
import re
from collections import Counter


TOKEN_RE = re.compile(r"\w+|[^\w\s]")
WORD_RE = re.compile(r"[a-z0-9]{3,}")

STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "your", "are", "not",
    "can", "will", "have", "has", "but", "into", "they", "their", "them", "you",
    "all", "one", "two", "three", "four", "five", "six", "how", "why", "what",
    "when", "where", "who", "which", "more", "most", "some", "any", "each",
    "every", "only", "also", "than", "then", "other", "such", "use", "using",
    "used", "make", "makes", "made", "instead", "without", "while", "works",
    "work", "system", "approach", "model", "idea", "concept", "option",
    "pillar", "element", "component", "alternative", "step", "phase", "tier",
}

CAUSAL_LEVER_KEYWORDS: dict[str, set[str]] = {
    "incentive_split_or_bounty": {
        "commission", "split", "bounty", "royalty", "spiff", "override", "fee",
        "escrow", "deposit", "credit", "reward", "bonus", "demurrage", "forfeiture",
    },
    "queue_or_lead_priority": {
        "rotation", "queue", "priority", "inbound", "lead", "leads", "freeze",
        "immunity", "fast", "express", "lane", "track", "triage",
    },
    "information_artifact_or_schema": {
        "tag", "qr", "menu", "zine", "card", "slip", "dossier", "ledger",
        "passport", "checklist", "manifest", "bundle", "cartridge", "template",
        "schema", "canonical",
    },
    "temporal_batch_or_inversion": {
        "batch", "window", "clock", "decay", "pre", "post", "before", "after",
        "parallel", "concurrent", "swarm", "milestone", "staged", "gate", "canary",
    },
    "role_or_boundary_separation": {
        "navigator", "specialist", "valet", "twin", "curator", "captain",
        "guild", "verifier", "bundler", "vestibule", "hub", "courier", "peer",
    },
    "subtraction_or_purge": {
        "sunset", "purge", "retire", "abolish", "delete", "shred", "subtract",
        "subtraction", "eliminate", "ban", "stop", "remove", "de-implementation",
    },
    "physical_or_sensor_constraint": {
        "nfc", "lockbox", "locker", "pouch", "opaque", "scale", "gravimetric",
        "camera", "photo", "360", "shield", "shielding", "drawer", "shelf", "tape",
    },
}


def count_tokens(text: str) -> int:
    return len(TOKEN_RE.findall(text))


def _stem(word: str) -> str:
    for suffix in (
        "ingly", "edly", "ment", "tion", "sion", "ness", "able", "ible",
        "ing", "ers", "ies", "ed", "es", "ly", "s",
    ):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            if suffix == "ies":
                return word[:-3] + "y"
            return word[: -len(suffix)]
    return word


def dominant_lever(text: str) -> str:
    lowered = set(WORD_RE.findall(text.lower()))
    best_lever = "general_process"
    best_score = 0
    for lever, kw_set in CAUSAL_LEVER_KEYWORDS.items():
        score = len(lowered & kw_set)
        if score > best_score:
            best_score = score
            best_lever = lever
    return best_lever


def content_features(text: str) -> Counter[str]:
    words = [_stem(w) for w in WORD_RE.findall(text.lower()) if w not in STOPWORDS]
    counts: Counter[str] = Counter()
    for w in words:
        if w not in STOPWORDS and len(w) >= 3:
            counts[f"w:{w}"] += 1.0
    for i in range(len(words) - 1):
        w1, w2 = sorted((words[i], words[i + 1]))
        if w1 != w2:
            counts[f"bg:{w1}_{w2}"] += 1.0
    lowered = set(WORD_RE.findall(text.lower()))
    for lever, kw_set in CAUSAL_LEVER_KEYWORDS.items():
        overlap = len(lowered & kw_set)
        if overlap:
            counts[f"lever:{lever}"] += 3.0 * overlap
    return counts


def cosine_similarity(c1: Counter[str], c2: Counter[str]) -> float:
    if not c1 or not c2:
        return 0.0
    dot = sum(v * c2.get(k, 0.0) for k, v in c1.items())
    n1 = math.sqrt(sum(v * v for v in c1.values()))
    n2 = math.sqrt(sum(v * v for v in c2.values()))
    if n1 == 0.0 or n2 == 0.0:
        return 0.0
    return max(0.0, min(1.0, dot / (n1 * n2)))


def _jacobi_eigenvalues(matrix: list[list[float]], max_sweeps: int = 50) -> list[float]:
    n = len(matrix)
    if n == 0:
        return []
    if n == 1:
        return [matrix[0][0]]
    a = [row[:] for row in matrix]
    for _ in range(max_sweeps):
        max_val = 0.0
        p, q = 0, 1
        for i in range(n):
            for j in range(i + 1, n):
                if abs(a[i][j]) > max_val:
                    max_val = abs(a[i][j])
                    p, q = i, j
        if max_val < 1e-10:
            break
        diff = a[q][q] - a[p][p]
        if abs(a[p][q]) < 1e-15:
            t = 0.0
        elif abs(diff) < 1e-12:
            t = 1.0 if a[p][q] > 0 else -1.0
        else:
            phi = diff / (2.0 * a[p][q])
            t = 1.0 / (abs(phi) + math.sqrt(phi * phi + 1.0))
            if phi < 0:
                t = -t
        c = 1.0 / math.sqrt(1.0 + t * t)
        s = t * c
        tau = s / (1.0 + c)
        apq = a[p][q]
        a[p][q] = 0.0
        a[q][p] = 0.0
        a[p][p] -= t * apq
        a[q][q] += t * apq
        for r in range(n):
            if r != p and r != q:
                arp = a[r][p]
                arq = a[r][q]
                a[r][p] = arp - s * (arq + tau * arp)
                a[p][r] = a[r][p]
                a[r][q] = arq + s * (arp - tau * arq)
                a[q][r] = a[r][q]
    return [max(0.0, a[i][i]) for i in range(n)]


def compute_vendi_score(texts: list[str]) -> float:
    n = len(texts)
    if n <= 1:
        return float(n)
    feats = [content_features(t) for t in texts]
    kernel = [[0.0] * n for _ in range(n)]
    for i in range(n):
        kernel[i][i] = 1.0 / n
        for j in range(i + 1, n):
            sim = cosine_similarity(feats[i], feats[j]) / n
            kernel[i][j] = sim
            kernel[j][i] = sim
    eigenvalues = _jacobi_eigenvalues(kernel)
    total = sum(eigenvalues)
    if total <= 0:
        return 1.0
    entropy = 0.0
    for lam in eigenvalues:
        p = lam / total
        if p > 1e-12:
            entropy -= p * math.log(p)
    return round(math.exp(entropy), 3)


def cluster_mechanisms(texts: list[str], similarity_threshold: float = 0.26) -> list[list[int]]:
    n = len(texts)
    if n == 0:
        return []
    feats = [content_features(t) for t in texts]
    levers = [dominant_lever(t) for t in texts]
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(n):
        for j in range(i + 1, n):
            sim = cosine_similarity(feats[i], feats[j])
            if sim >= similarity_threshold or (levers[i] == levers[j] and sim >= 0.16):
                union(i, j)

    groups: dict[int, list[int]] = {}
    for idx in range(n):
        root = find(idx)
        groups.setdefault(root, []).append(idx)
    return list(groups.values())


def extract_candidate_mechanisms(markdown_text: str) -> list[dict[str, str]]:
    """Extract top-level candidate mechanism blocks from a portfolio response."""
    lines = markdown_text.splitlines()
    heading_re = re.compile(
        r"^(#{2,4})\s+(?:"
        r"(?:Approach|Alternative|Portfolio\s+(?:Component|Element)|Movement|Concept|Idea|Possibility)\s+[A-Z0-9]+[:.\s—-]*|"
        r"(?:[0-9]+\.[0-9]+|[0-9]+|[A-I])[.)\s:—-]+"
        r")(.+)$",
        re.IGNORECASE,
    )
    ignore_titles = (
        "executive", "summary", "diagnos", "comparison", "matrix", "roadmap",
        "rollout", "phased", "immediate", "where to start", "how to start",
        "key takeaway", "prioritization", "constraint", "guardrail", "strategic",
        "target assumption", "taken-for-granted", "formal provocations",
        "provocations (po", "system architecture", "integrated", "recommended",
        "systemic failure", "four-part", "4-part", "4-pillar", "portfolio of",
    )

    sections: list[tuple[str, list[str]]] = []
    cur_title: str | None = None
    cur_lines: list[str] = []

    for line in lines:
        m = heading_re.match(line.strip())
        if m:
            title = m.group(2).strip().strip("*")
            if any(ig in title.lower() for ig in ignore_titles):
                if cur_title and cur_lines:
                    sections.append((cur_title, cur_lines))
                cur_title = None
                cur_lines = []
                continue
            if cur_title and cur_lines:
                sections.append((cur_title, cur_lines))
            cur_title = title
            cur_lines = []
        elif line.strip().startswith("## ") and cur_title:
            if any(ig in line.lower() for ig in ignore_titles):
                sections.append((cur_title, cur_lines))
                cur_title = None
                cur_lines = []
        else:
            if cur_title is not None:
                cur_lines.append(line)

    if cur_title and cur_lines:
        sections.append((cur_title, cur_lines))

    candidates: list[dict[str, str]] = []
    for title, body_lines in sections:
        body_text = "\n".join(body_lines).strip()
        if len(body_text) >= 40:
            candidates.append({
                "title": title,
                "lever": dominant_lever(f"{title} {body_text}"),
                "text": f"{title}: {body_text}",
            })
    return candidates
