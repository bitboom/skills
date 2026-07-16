# Research basis

These sources explain the design. They are maintenance references and need not be loaded during ordinary runs.

- Self-Refine supports iterative feedback and revision, but does not by itself guarantee factuality: https://arxiv.org/abs/2303.17651
- CRITIC motivates tool-grounded critique instead of unsupported introspection: https://arxiv.org/abs/2305.11738
- Chain-of-Verification motivates independent verification questions before final synthesis: https://arxiv.org/abs/2309.11495
- Iterative self-refinement can reward-hack an imperfect model judge, especially when author and evaluator share context: https://arxiv.org/abs/2407.04549
- D3 motivates role-specialized deliberation instead of one undifferentiated evaluator: https://arxiv.org/abs/2410.04663
- Summarization research separates coherence and concision from informativeness and faithfulness: https://arxiv.org/abs/2606.08000
- iRULER motivates explicit criteria, score justification, and actionable revision targets: https://arxiv.org/abs/2602.12779
- ReviewGrounder motivates rubric-guided, tool-integrated, evidence-grounded review: https://arxiv.org/abs/2604.14261
- LLM-as-a-Judge reliability work documents position, verbosity, and self-preference biases: https://arxiv.org/html/2411.15594
- In-place expert feedback motivates exact issue-local edits over diffuse conversational revision: https://arxiv.org/abs/2510.00777

Public workflow references:

- Agent Skills specification: https://agentskills.io/specification
- Vercel skills CLI discovery: https://github.com/vercel-labs/skills
- Matt Pocock's small, composable skill library: https://github.com/mattpocock/skills
- Verification Before Completion's evidence-before-claims gate: https://github.com/obra/superpowers/tree/main/skills/verification-before-completion
- Anthropic's public PPTX skill demonstrates text extraction and rendered visual inspection. Its repository marks the skill proprietary, so copy no text or code: https://github.com/anthropics/skills/tree/main/skills/pptx
