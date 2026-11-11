"""Web interface for the landscape generator.

Contents:
    app        - FastAPI app: front end (static/) + JSON API under /api; STATIC_ENDPOINTS for the Pages export
    reference  - Python reference landscapes (height map + colour map) for the Python-vs-JS Verify page
    static/    - ES-module front end; terrain_engine.js and friends are a bit-exact JS port of the
                 terrain package (numpy.random PCG64 + ziggurat, noise, features, biomes)
"""
