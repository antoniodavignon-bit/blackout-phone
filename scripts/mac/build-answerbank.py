#!/usr/bin/env python3
"""
build-answerbank.py — runs on the MAC. Builds the question bridge.

The phone cannot reason about its library. Measured in Phase 03: prompt
processing is 6.1 tok/s, so a five-passage RAG prompt takes 5.5 minutes to
READ before generating anything. Runtime inference on-device is not slow,
it is impossible.

So inference happens here, once, and the artifact is carried.

What this does NOT do: generate an answer for every article. Plain text comes
out at 5.68x the ZIM size — the 18 GiB library is ~104 GB of text across more
than a million articles. That is roughly 58 days of generation. Not scoped
down; abandoned.

What it DOES: the ZIMs already contain a Xapian full-text index that answers
queries in 1-12 ms. That index works perfectly — if you already know the
expert term. Asked naturally, it fails:

    "how do I make drinking water safe" -> PFAS timeline, Bleach, Lead abatement
    "water chlorination"                -> Water chlorination, Shock chlorination

The library is fine. The door is broken. This builds the door: natural
question -> expert query -> the article that answers it -> a short answer
written from that article's actual text.

Bounded by questions asked (thousands), not articles stored (millions).
Measured cost: 4,915 bytes per question. 20,000 questions is 98 MB.

Usage:
    ./build-answerbank.py --zim ~/Downloads/blackout-library/Kiwix/*.zim \\
                          --questions questions.txt \\
                          --out answerbank.sqlite \\
                          --model llama3.1:8b
"""
import argparse, json, os, re, sqlite3, sys, time
import urllib.request

TAG = re.compile(r"<[^>]+>")
WS  = re.compile(r"\s+")
OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")


def ollama(model, prompt, timeout=180):
    req = urllib.request.Request(
        f"{OLLAMA}/api/generate",
        data=json.dumps({"model": model, "prompt": prompt, "stream": False}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())["response"].strip()


def article_text(archive, path, limit=6000):
    try:
        html = bytes(archive.get_entry_by_path(path).get_item().content).decode("utf-8", "ignore")
    except Exception:
        return ""
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    return WS.sub(" ", TAG.sub(" ", html)).strip()[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zim", nargs="+", required=True)
    ap.add_argument("--questions", required=True, help="one natural question per line")
    ap.add_argument("--out", default="answerbank.sqlite")
    ap.add_argument("--model", default="llama3.1:8b")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    from libzim.reader import Archive
    from libzim.search import Query, Searcher

    archives = []
    for p in a.zim:
        try:
            arc = Archive(p)
            archives.append((os.path.basename(p), arc))
            print(f"  opened {os.path.basename(p)}  "
                  f"articles={arc.article_count:,}  fulltext={arc.has_fulltext_index}")
        except Exception as e:
            print(f"  SKIP {p}: {e}", file=sys.stderr)
    if not archives:
        sys.exit("no ZIMs opened")

    questions = [q.strip() for q in open(a.questions) if q.strip() and not q.startswith("#")]
    if a.limit:
        questions = questions[: a.limit]
    print(f"  {len(questions)} questions\n")

    if os.path.exists(a.out):
        os.remove(a.out)
    db = sqlite3.connect(a.out)
    db.execute("CREATE VIRTUAL TABLE qa USING fts5("
               "question, expert_query, answer, article, zim, unindexed_ok UNINDEXED)")

    t_start = time.time()
    written = skipped = 0
    for i, q in enumerate(questions, 1):
        # 1. translate the question into the vocabulary the index actually uses
        expert = ollama(a.model,
            "Rewrite this question as 2-5 words of technical search vocabulary — the "
            "words an encyclopedia article on the subject would use in its title. "
            "Output ONLY those words, nothing else.\n\n"
            f"Question: {q}\nSearch terms:")
        expert = expert.strip().strip('".').splitlines()[0][:80]

        # 2. retrieve with the expert terms, across every archive
        best = None
        for name, arc in archives:
            if not arc.has_fulltext_index:
                continue
            try:
                res = Searcher(arc).search(Query().set_query(expert))
                hits = list(res.getResults(0, 1))
            except Exception:
                continue
            if hits:
                best = (name, arc, hits[0])
                break
        if not best:
            print(f"  [{i}/{len(questions)}] no hit: {q!r} (terms: {expert!r})")
            skipped += 1
            continue

        name, arc, path = best
        title = arc.get_entry_by_path(path).title
        body = article_text(arc, path)
        if len(body) < 200:
            skipped += 1
            continue

        # 3. write the answer FROM the retrieved text, not from model memory
        answer = ollama(a.model,
            "Answer the question using ONLY the source text below. Be direct and "
            "practical — this is read on a 2.8 inch screen in an emergency. Three "
            "sentences maximum. If the source does not answer it, reply exactly: "
            "NOT IN SOURCE.\n\n"
            f"Question: {q}\n\nSource ({title}):\n{body}\n\nAnswer:")

        if answer.strip().upper().startswith("NOT IN SOURCE"):
            print(f"  [{i}/{len(questions)}] ungrounded, dropped: {q!r}")
            skipped += 1
            continue

        db.execute("INSERT INTO qa VALUES (?,?,?,?,?,?)",
                   (q, expert, answer, title, name, ""))
        written += 1
        if i % 25 == 0:
            db.commit()
            el = time.time() - t_start
            print(f"  [{i}/{len(questions)}] {written} written, {skipped} dropped, "
                  f"{el/i:.1f}s/question, ETA {(len(questions)-i)*el/i/60:.0f} min")

    db.commit()
    size = os.path.getsize(a.out)
    print(f"\n  wrote {a.out}")
    print(f"  {written} answers, {skipped} dropped")
    print(f"  {size:,} bytes ({size/max(written,1):,.0f} bytes/answer)")
    print(f"  {(time.time()-t_start)/60:.1f} minutes")
    print("\n  copy to the card at Reference/answerbank.sqlite")


if __name__ == "__main__":
    main()
