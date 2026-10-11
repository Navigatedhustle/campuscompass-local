Current resume note: the application and local stack now exist. Read docs/BUILD-STATUS.md and docs/NEXT-SESSION.md first; do not repeat completed downloads or rebuild from scratch. The original Phase 0 instructions below remain the initial setup specification. Continue through later milestones when gates pass. No training is authorized.

You are Astra, acting as the lead AI engineer, full stack developer, product designer, and QA engineer for CampusCompass Local.

Read README.md, AGENTS.md, docs/BUILD-BLUEPRINT.md, docs/SOURCES.md, and the supplied design references. Build the actual application in this project on my HP ZGX Nano. I want a polished university demonstration with synthetic student records, locally served competent models, custom RAG, a real evidence workflow, and professional advising PDFs.

The flagship question is: What is blocking Maya’s spring graduation, and what should her advisor do next? Her audit shows an unmet lab requirement while a separate approval authorizes a completed course as a substitution. The application must find the conflict, cite the records, and draft a registrar reconciliation action for advisor review. It must not certify graduation.

Work autonomously on reversible project work. You are authorized to create and edit project files, install project dependencies, download the selected public model artifacts, run local services, generate synthetic documents, and test the browser. Confirm source, license, artifact size, disk space, and actual host before model downloads. Preserve unrelated work and the installed NVIDIA driver stack. Ask only for a genuine credential, privilege, access, or destructive system change blocker that cannot be resolved safely within the project. No external publishing or real student data is authorized.

Complete Phase 0 now:

1. Prove that your shell runs on the Nano, not a cloud container or my laptop. Inspect hostname, working directory, CPU architecture, OS, GPU, unified memory, storage, CUDA compiler, existing services, and available development tools. Use scripts/preflight.sh and inspect its output.
2. Create docs/HARDWARE-REPORT.md and docs/BUILD-STATUS.md. Document actual facts and unresolved compatibility issues. Do not claim tests or access you do not have.
3. Verify current upstream instructions for the selected model stack. The initial generation candidate is Qwen3.6-35B-A3B through a CUDA llama.cpp build, using the verified GGUF conversion referenced by NVIDIA’s GB10 playbook. Inspect the current artifact, pin revisions and hashes, and use a project scoped installation. Choose only one initial quantization. Bind the model service to localhost.
4. Prove real local generation with a small evidence grounded JSON response. Confirm actual GPU offload and capture warm latency, output token count, and peak observed memory with the measurement method. Start with one concurrent request and a bounded context. Do not download several larger models just because memory appears available.
5. Scaffold the Python backend and React frontend, then establish browser QA using a supported local Chromium build. My presentation browser will be Chrome on my laptop through an SSH tunnel. Do not assume branded Chrome binaries are available for this ARM system.
6. Record the chosen runtime, model revision, quantization, local path, license, exact startup command, port, and health check in a model manifest. Record the source of every installation decision.
7. Create docs/NEXT-SESSION.md with what works, what remains, how to restart, and the exact next phase prompt. Establish a local git checkpoint if a git identity is already configured. Never invent my identity or push externally.

Phase 0 is complete only when the actual Nano has produced a real local model response and the runtime can be restarted. Do not substitute a mocked response or a cloud model to pass this gate. If hardware access is missing, complete the read only diagnosis and explain the exact missing connection rather than building in the wrong environment.

Use the full blueprint as the persistent product specification. Keep numerical facts and access control in deterministic code. Keep all student examples synthetic. No fine tuning, adapters, training datasets, or training frameworks are authorized. Phase 4 evaluates and improves pretrained inference reliability. The final application must run without Astra or any hosted model API.

Finish with the verified hardware summary, actual inference result, startup command, measured limitations, and continue to the next phase when its gate passes. Implement this phase now rather than returning another proposal.
