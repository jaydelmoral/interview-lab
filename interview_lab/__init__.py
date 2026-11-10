"""Interview Lab: local-first interview practice with hidden-test grading and tailored exam simulations.

Layers (dependencies point inward, see docs/architecture/):
    web (HTTP)  ->  application (use cases + ports)  ->  domain (pure rules)
    adapters (filesystem, JVM, HTTP fetch, AI) implement the ports defined in application.
"""
__version__ = "1.0.0"
