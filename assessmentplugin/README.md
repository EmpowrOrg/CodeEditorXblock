# Assessment XBlock

Renders a Coppin assessment as an interactive, student-facing quiz inside Open edX. The UI is a
self-contained React component — **the same `AssessmentPlayer` the Coppin teacher app uses for its
"Live preview"** — so what authors preview is exactly what students get. It does **not** use Paragon.

Interactive only: students can answer every question type (Multiple Choice, Checkbox, True/False,
Text Input, Number Input, Short Answer, Long Answer) and their answers are saved to user state. It
does not auto-grade.

## Layout

```
assessmentplugin/
  setup.py                         # entry point: assessmentplugin = assessmentplugin:AssessmentXBlock
  assessmentplugin/
    assessmentplugin.py            # the XBlock (fields, student_view, JSON handlers)
    static/
      html/assessmentplugin.html   # mount point
      css/assessmentplugin.css     # container only; component styles are injected by React
      js/dist/bundle.js            # built React bundle (commit this)
  frontend/                        # React source for the bundle
    src/
      AssessmentPlayer.tsx         # VENDORED copy of the canonical component (see below)
      index.tsx                    # edX entry: window.AssessmentXBlock(runtime, element, initArgs)
    esbuild.mjs                    # bundles src/index.tsx -> ../assessmentplugin/static/js/dist/bundle.js
    package.json / tsconfig.json
```

## The shared component

`frontend/src/AssessmentPlayer.tsx` is a **byte-for-byte copy** of the canonical source in the
Coppin teacher frontend:

```
coppin-frontend/src/shared/assessment/AssessmentPlayer.tsx   <-- canonical, edit here
CodeEditorXblock/assessmentplugin/frontend/src/AssessmentPlayer.tsx   <-- vendored copy
```

It is React-only (no MUI, no Paragon, no CSS framework — styles are injected once into `<head>`,
scoped under `.coppin-asmt-*`). When you change the canonical file, copy it over and rebuild:

```bash
cp ../../../coppin-frontend/src/shared/assessment/AssessmentPlayer.tsx frontend/src/AssessmentPlayer.tsx
cd frontend && npm run build
```

## Build the frontend

```bash
cd frontend
npm install
npm run build      # writes ../assessmentplugin/static/js/dist/bundle.js
npm run watch      # rebuild on change while developing
npm run typecheck  # tsc --noEmit
```

## Install the XBlock

From the repo root (same pattern as `swiftplugin`):

```bash
pip install -e assessmentplugin
```

Then add `assessmentplugin` to the course's **Advanced Module List** in Studio and drop in an
"Assessment" component. In Tutor: `tutor mounts add .` and rebuild `openedx-dev`.

## Configure (Studio → Edit)

| Field            | Meaning                                                              |
|------------------|---------------------------------------------------------------------|
| `display_name`   | Name in the unit outline.                                            |
| `reference_id`   | Coppin assessment / lesson-item id to load.                         |
| `api_url`        | Base URL of the Coppin public API.                                  |
| `api_key`        | Coppin application API key (sent as `Authorization: Bearer <key>`). |
| `assessment_path`| Path appended to `api_url` to fetch the assessment (default `assessment`). |

If `api_url`, `reference_id`, and `api_key` are not all set, the block renders a built-in
**sample assessment** (all 7 question types) so it works in the workbench out of the box.

## Backend contract

`get_assessment` POSTs `{ referenceId, studentId, blockId }` with the Bearer key to
`<api_url>/<assessment_path>` and expects either a bare assessment object or `{ "assessment": {…} }`:

```jsonc
{
  "id": "…", "title": "…", "expectedCompletionTimeInMinutes": 15,
  "problems": [
    { "id": "…", "type": "MultipleChoice", "prompt": "…", "points": 1,
      "options": [ { "id": "…", "text": "…", "order": 0, "isCorrect": true } ] },
    { "id": "…", "type": "TextInput", "prompt": "…", "points": 1, "answer": "…" }
    // types: MultipleChoice | Checkbox | TrueFalse | TextInput | NumberInput | ShortAnswer | LongAnswer
  ]
}
```

`isCorrect`/`answer` are ignored by the player (interactive only). `save_answers` POSTs
`{ answers: { problemId: value | [optionIds] } }`, stored in `Scope.user_state`.

> **TODO (backend):** add the public `<assessment_path>` endpoint to Coppin that resolves a
> `referenceId` to this shape, scoped by the application key's organization. Until then the block
> uses the sample fallback.
