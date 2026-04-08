This repo contains a collection of agent skills for capturing, summarizing, and querying information. Inputs can be user notes or other reference documents. Agent skill reference information can be found in [docs/skill_references](docs/skill_references).

When deployed, agents will only have access to the [skills](skills) directory. Skills will be loaded when the descriptions match the current situation in the agent's opinion. The agent will then read the rest of the skill and any supporting documentation the skill references when needed. The agent follows the rules/process described in the skill and performs the actions.

Skills should be standalone. They must fully provide context the calling agent to perform the actions described. Skills may reference other external/shared documents if required to aid in progressive disclosure (only providing context when required), and reduce duplication across the repo.

All information the agent needs must be contained in the skills directory and properly referenced from that file to other reference files.

Any files in this repo that are not in the [skills](skills) directory or directly referenced by a skill will not be available to the agent for skills. Directories like [docs](docs) and [tests](tests) are only meant to be used for reference during development.
