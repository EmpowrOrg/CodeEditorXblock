/**
 * edX entry point. The Python XBlock calls `initialize_js('AssessmentXBlock', json_args)`, which
 * invokes the global function below with (runtime, element, initArgs). We mount the shared
 * AssessmentPlayer, load the assessment via the `get_assessment` handler, and persist answers via
 * `save_answers` as the student works (debounced). Interactive only — no grading.
 */
import {createElement} from "react";
import {createRoot, type Root} from "react-dom/client";
import {AssessmentPlayer, type AssessmentAnswers, type AssessmentPlayerData} from "./AssessmentPlayer";

interface Runtime {
    handlerUrl: (element: HTMLElement, handler: string) => string;
}

interface InitArgs {
    answers?: AssessmentAnswers;
}

function postJson(url: string, body: unknown): Promise<any> {
    return fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body ?? {}),
    }).then((r) => r.json());
}

function AssessmentXBlock(runtime: Runtime, element: HTMLElement, initArgs: InitArgs = {}) {
    const mount = (element.querySelector(".coppin-asmt-mount") as HTMLElement) || element;
    const root: Root = createRoot(mount);

    const getUrl = runtime.handlerUrl(element, "get_assessment");
    const saveUrl = runtime.handlerUrl(element, "save_answers");

    let answers: AssessmentAnswers = initArgs.answers || {};
    let saveTimer: number | undefined;

    const persist = (next: AssessmentAnswers) => {
        answers = next;
        if (saveTimer) window.clearTimeout(saveTimer);
        // Debounce so typing doesn't fire a request per keystroke.
        saveTimer = window.setTimeout(() => {
            postJson(saveUrl, {answers: next}).catch(() => {/* best-effort */});
        }, 600);
    };

    const renderPlayer = (assessment: AssessmentPlayerData) => {
        root.render(createElement(AssessmentPlayer, {
            assessment,
            defaultValue: answers,
            onChange: persist,
        }));
    };

    const renderMessage = (cls: string, text: string) => {
        root.render(createElement("div", {className: cls}, text));
    };

    renderMessage("coppin-asmt-loading", "Loading assessment…");

    postJson(getUrl, {})
        .then((d) => {
            if (d && d.error) {
                renderMessage("coppin-asmt-error", d.error);
            } else if (d && d.assessment) {
                renderPlayer(d.assessment as AssessmentPlayerData);
            } else {
                renderMessage("coppin-asmt-error", "No assessment was returned.");
            }
        })
        .catch(() => renderMessage("coppin-asmt-error", "Could not load this assessment."));
}

// Expose for edX's `initialize_js`.
(window as unknown as Record<string, unknown>).AssessmentXBlock = AssessmentXBlock;

export default AssessmentXBlock;
