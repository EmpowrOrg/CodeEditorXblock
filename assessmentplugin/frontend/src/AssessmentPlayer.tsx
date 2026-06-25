/**
 * AssessmentPlayer — the student-facing, interactive view of a Coppin assessment.
 *
 * CANONICAL SOURCE. This file is intentionally dependency-free (React only): no MUI, no Paragon,
 * no CSS framework. All styling is injected once into <head> scoped under `.coppin-asmt-*`, so the
 * component renders identically wherever it is mounted. It is vendored VERBATIM into the edX
 * Assessment XBlock frontend (CodeEditorXblock/assessmentplugin/frontend/src/AssessmentPlayer.tsx)
 * so the teacher's "Live preview" and the real student view stay in lockstep.
 *
 * Keep this file import-free beyond `react` and avoid React 18+/19-only APIs (e.g. useId) so it
 * drops into any React 17+ host. Interactive only: every question type is answerable, but nothing
 * is graded or scored here.
 *
 * If you change this file, copy it to the XBlock vendored path (they must stay byte-identical).
 */
import {useEffect, useMemo, useRef, useState} from "react";

export type AssessmentQuestionType =
    | "MultipleChoice"
    | "TextInput"
    | "Checkbox"
    | "NumberInput"
    | "ShortAnswer"
    | "LongAnswer"
    | "TrueFalse";

export interface AssessmentPlayerOption {
    id: string;
    text: string;
    order?: number;
    /** Present in authoring data; ignored in this interactive-only player. */
    isCorrect?: boolean;
}

export interface AssessmentPlayerProblem {
    id: string;
    type: AssessmentQuestionType;
    prompt: string;
    points?: number;
    options?: AssessmentPlayerOption[] | null;
    /** Authoring sample/correct answer; ignored here. */
    answer?: string | null;
    imageUrl?: string | null;
}

export interface AssessmentPlayerData {
    id?: string;
    title?: string;
    problems: AssessmentPlayerProblem[];
    expectedCompletionTimeInMinutes?: number;
}

/** problemId -> answer. A string for single-value types; string[] of option ids for Checkbox. */
export type AssessmentAnswers = Record<string, string | string[]>;

export interface AssessmentPlayerProps {
    assessment: AssessmentPlayerData;
    /** Controlled answer map. When provided, `onChange` is the only way state changes. */
    value?: AssessmentAnswers;
    /** Initial answers for uncontrolled usage. */
    defaultValue?: AssessmentAnswers;
    /** Fired whenever the student edits an answer. */
    onChange?: (answers: AssessmentAnswers) => void;
    /** Render every input read-only / disabled. */
    disabled?: boolean;
    /** Hide the built-in title row (the host already shows one). */
    hideTitle?: boolean;
}

const STYLE_ID = "coppin-asmt-styles";
const STYLES = `
.coppin-asmt-root{--asmt-fg:#1a1a1a;--asmt-muted:#5f6368;--asmt-border:#d7dbe0;--asmt-accent:#2563eb;--asmt-card:#fff;--asmt-bg-soft:#f5f7fa;color:var(--asmt-fg);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.5;font-size:15px;box-sizing:border-box}
.coppin-asmt-root *,.coppin-asmt-root *::before,.coppin-asmt-root *::after{box-sizing:inherit}
.coppin-asmt-title{font-size:1.25rem;font-weight:700;margin:0 0 .25rem}
.coppin-asmt-meta{color:var(--asmt-muted);font-size:.85rem;margin:0 0 1rem}
.coppin-asmt-q{background:var(--asmt-card);border:1px solid var(--asmt-border);border-radius:10px;padding:1rem 1.1rem;margin-bottom:.9rem}
.coppin-asmt-qhead{display:flex;align-items:flex-start;gap:.5rem;margin-bottom:.6rem}
.coppin-asmt-qnum{font-weight:700;white-space:nowrap}
.coppin-asmt-prompt{flex:1;font-weight:600}
.coppin-asmt-pts{flex-shrink:0;font-size:.72rem;font-weight:600;color:var(--asmt-muted);background:var(--asmt-bg-soft);border:1px solid var(--asmt-border);border-radius:999px;padding:.1rem .55rem}
.coppin-asmt-img{max-width:100%;border-radius:8px;margin:.25rem 0 .75rem;display:block}
.coppin-asmt-opt{display:flex;align-items:flex-start;gap:.55rem;padding:.45rem .55rem;border:1px solid var(--asmt-border);border-radius:8px;margin-bottom:.45rem;cursor:pointer;transition:border-color .12s,background .12s}
.coppin-asmt-opt:hover{border-color:var(--asmt-accent);background:var(--asmt-bg-soft)}
.coppin-asmt-opt.is-checked{border-color:var(--asmt-accent);background:#eff4ff}
.coppin-asmt-opt input{margin-top:.2rem;accent-color:var(--asmt-accent);width:1rem;height:1rem;flex-shrink:0}
.coppin-asmt-opt-text{flex:1}
.coppin-asmt-input,.coppin-asmt-textarea{width:100%;font:inherit;color:inherit;border:1px solid var(--asmt-border);border-radius:8px;padding:.55rem .65rem;background:var(--asmt-card)}
.coppin-asmt-input:focus,.coppin-asmt-textarea:focus{outline:none;border-color:var(--asmt-accent);box-shadow:0 0 0 3px rgba(37,99,235,.15)}
.coppin-asmt-textarea{resize:vertical;min-height:4.5rem}
.coppin-asmt-hint{color:var(--asmt-muted);font-size:.78rem;margin-top:.35rem}
.coppin-asmt-root [disabled],.coppin-asmt-root.is-disabled .coppin-asmt-opt{cursor:not-allowed;opacity:.7}
.coppin-asmt-empty{color:var(--asmt-muted);font-style:italic;padding:1rem 0}
`;

/** Inject the scoped stylesheet once per document (works in the SPA and the XBlock iframe alike). */
function useInjectedStyles(): void {
    useEffect(() => {
        if (typeof document === "undefined") return;
        if (document.getElementById(STYLE_ID)) return;
        const el = document.createElement("style");
        el.id = STYLE_ID;
        el.textContent = STYLES;
        document.head.appendChild(el);
    }, []);
}

let instanceCounter = 0;

const sortedOptions = (p: AssessmentPlayerProblem): AssessmentPlayerOption[] => {
    const opts = (p.options ?? []).slice();
    opts.sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
    return opts;
};

/** True/False questions may arrive without options; synthesize them so the UI is consistent. */
const trueFalseOptions = (p: AssessmentPlayerProblem): AssessmentPlayerOption[] => {
    const opts = sortedOptions(p);
    if (opts.length >= 2) return opts;
    return [
        {id: `${p.id}-true`, text: "True"},
        {id: `${p.id}-false`, text: "False"},
    ];
};

export function AssessmentPlayer(props: AssessmentPlayerProps) {
    const {assessment, value, defaultValue, onChange, disabled = false, hideTitle = false} = props;
    useInjectedStyles();

    const name = useMemo(() => `coppin-asmt-${++instanceCounter}`, []);
    const controlled = value !== undefined;
    const [internal, setInternal] = useState<AssessmentAnswers>(defaultValue ?? {});
    const answers = controlled ? value! : internal;

    // Keep a ref so we always merge against the latest answers without re-subscribing handlers.
    const answersRef = useRef(answers);
    answersRef.current = answers;

    const setAnswer = (problemId: string, next: string | string[]) => {
        const merged: AssessmentAnswers = {...answersRef.current, [problemId]: next};
        if (!controlled) setInternal(merged);
        onChange?.(merged);
    };

    const toggleCheckbox = (problemId: string, optionId: string) => {
        const cur = answersRef.current[problemId];
        const arr = Array.isArray(cur) ? cur : [];
        const next = arr.includes(optionId) ? arr.filter((x) => x !== optionId) : [...arr, optionId];
        setAnswer(problemId, next);
    };

    const problems = assessment?.problems ?? [];

    return (
        <div className={`coppin-asmt-root${disabled ? " is-disabled" : ""}`}>
            {!hideTitle && assessment?.title && <h2 className="coppin-asmt-title">{assessment.title}</h2>}
            {!hideTitle && typeof assessment?.expectedCompletionTimeInMinutes === "number" && (
                <p className="coppin-asmt-meta">
                    {problems.length} question{problems.length === 1 ? "" : "s"} ·
                    ~{assessment.expectedCompletionTimeInMinutes} min
                </p>
            )}

            {problems.length === 0 && <div className="coppin-asmt-empty">This assessment has no questions yet.</div>}

            {problems.map((p, i) => {
                const a = answers[p.id];
                const single = typeof a === "string" ? a : "";
                const multi = Array.isArray(a) ? a : [];

                return (
                    <div className="coppin-asmt-q" key={p.id}>
                        <div className="coppin-asmt-qhead">
                            <span className="coppin-asmt-qnum">Q{i + 1}</span>
                            <span className="coppin-asmt-prompt">{p.prompt}</span>
                            {typeof p.points === "number" && (
                                <span className="coppin-asmt-pts">{p.points} pt{p.points === 1 ? "" : "s"}</span>
                            )}
                        </div>

                        {p.imageUrl && <img className="coppin-asmt-img" src={p.imageUrl} alt=""/>}

                        {(p.type === "MultipleChoice" || p.type === "TrueFalse") && (
                            <div role="radiogroup" aria-label={p.prompt}>
                                {(p.type === "TrueFalse" ? trueFalseOptions(p) : sortedOptions(p)).map((o) => {
                                    const checked = single === o.id;
                                    return (
                                        <label key={o.id} className={`coppin-asmt-opt${checked ? " is-checked" : ""}`}>
                                            <input
                                                type="radio"
                                                name={`${name}-${p.id}`}
                                                value={o.id}
                                                checked={checked}
                                                disabled={disabled}
                                                onChange={() => setAnswer(p.id, o.id)}
                                            />
                                            <span className="coppin-asmt-opt-text">{o.text}</span>
                                        </label>
                                    );
                                })}
                            </div>
                        )}

                        {p.type === "Checkbox" && (
                            <div role="group" aria-label={p.prompt}>
                                {sortedOptions(p).map((o) => {
                                    const checked = multi.includes(o.id);
                                    return (
                                        <label key={o.id} className={`coppin-asmt-opt${checked ? " is-checked" : ""}`}>
                                            <input
                                                type="checkbox"
                                                value={o.id}
                                                checked={checked}
                                                disabled={disabled}
                                                onChange={() => toggleCheckbox(p.id, o.id)}
                                            />
                                            <span className="coppin-asmt-opt-text">{o.text}</span>
                                        </label>
                                    );
                                })}
                            </div>
                        )}

                        {p.type === "TextInput" && (
                            <input
                                className="coppin-asmt-input"
                                type="text"
                                value={single}
                                disabled={disabled}
                                placeholder="Your answer"
                                onChange={(e) => setAnswer(p.id, e.target.value)}
                            />
                        )}

                        {p.type === "NumberInput" && (
                            <input
                                className="coppin-asmt-input"
                                type="number"
                                value={single}
                                disabled={disabled}
                                placeholder="Your answer"
                                onChange={(e) => setAnswer(p.id, e.target.value)}
                            />
                        )}

                        {p.type === "ShortAnswer" && (
                            <textarea
                                className="coppin-asmt-textarea"
                                rows={3}
                                value={single}
                                disabled={disabled}
                                placeholder="Write a short response"
                                onChange={(e) => setAnswer(p.id, e.target.value)}
                            />
                        )}

                        {p.type === "LongAnswer" && (
                            <textarea
                                className="coppin-asmt-textarea"
                                rows={8}
                                value={single}
                                disabled={disabled}
                                placeholder="Write your response"
                                onChange={(e) => setAnswer(p.id, e.target.value)}
                            />
                        )}
                    </div>
                );
            })}
        </div>
    );
}

export default AssessmentPlayer;
