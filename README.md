# Spyfall Environment

## Overview
This project develops a multi-agent social deduction game for AI research, inspired by Facebook Research's Cicero. The goal of this environment is to provide a framework for evaluating the ability of agents to craft and detect deceptive behavior in a social setting. For related work I found interesting, see:
- [Human-level play in the game of Diplomacy by combining language models with strategic reasoning](https://noambrown.github.io/papers/22-Science-Diplomacy-TR.pdf)
- [How to Catch an AI Liar: Lie Detection in Black-Box LLMs by Asking Unrelated Questions](https://arxiv.org/pdf/2309.15840)
- [Hoodwinked: Deception and Cooperation in a Text-Based Game for Language Models](https://arxiv.org/abs/2308.01404)

## Features
- Multi-agent gameplay
- Dialogue interactions to deduce roles and strategies.
- Integration with OpenAI's GPT models for generating responses.
- Interactive simulation of environment. `python -m spyfall.environment.interactive`

## Current Implementation
- Dialogue agents that respond based on game state and past interactions.
- Game environment management for roles, locations, and actions.

## Future Directions
- Enhance dialogue and action modules for complex reasoning based on dialogue.
- Lie detection and suspicion modules.
- Develop a MARL model that can play the game.

## Contributions
Feel free to clone the repository, make improvements, and submit a pull request.
