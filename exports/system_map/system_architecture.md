# Arkansas Civics Platform — System Architecture

## Content Library

- .yaml: 108 files
- .md: 1221 files

## Engine Modules

- engine\ai_assistant.py
- engine\api_server.py
- engine\auth_tokens.py
- engine\certification_rules.py
- engine\civic_credential_engine.py
- engine\civic_data_intelligence_engine.py
- engine\civic_intelligence_map.py
- engine\civic_intelligence_system.py
- engine\civic_knowledge_graph_expansion_engine.py
- engine\civic_mentor_engine.py
- engine\course_engine.py
- engine\database_engine.py
- engine\identity_manager.py
- engine\kernel_config.py
- engine\kernel_contracts.py
- engine\kernel_health.py
- engine\kernel_logger.py
- engine\knowledge_graph_engine.py
- engine\learning_analytics_engine.py
- engine\learning_runtime.py
- engine\lesson_player.py
- engine\library_loader.py
- engine\migration_engine.py
- engine\permissions_engine.py
- engine\platform_kernel.py
- engine\progress_engine.py
- engine\progress_registry.py
- engine\track_engine.py
- engine\user_identity_engine.py
- engine\__init__.py

## Build Scripts

- scripts\ai_course_designer.py
- scripts\build_all.py
- scripts\build_arkansas_civic_dataset.py
- scripts\build_arkansas_offline_dataset.py
- scripts\build_book.py
- scripts\build_civic_intelligence_map.py
- scripts\build_civic_intelligence_system.py
- scripts\build_civic_library.py
- scripts\build_course_engine.py
- scripts\build_course_exports.py
- scripts\build_knowledge_graph.py
- scripts\build_learning_analytics.py
- scripts\build_lesson_player.py
- scripts\build_phase_01_core_kernel.py
- scripts\build_phase_02_identity.py
- scripts\build_phase_03_progress_credentials.py
- scripts\build_phase_04_database.py
- scripts\build_phase_06_graph_expansion.py
- scripts\build_phase_07_graph_persistence.py
- scripts\build_track_engine.py
- scripts\cleanup_repo.py
- scripts\copy_dashboard_content.py
- scripts\editor_dashboard_generator.py
- scripts\export_rise_course.py
- scripts\fix_phase07_future_imports_properly.py
- scripts\fix_phase07_imports.py
- scripts\full_repo_audit.py
- scripts\generate_reader_site.py
- scripts\influence_analyzer.py
- scripts\kernel_health_check.py
- scripts\load_graph_to_supabase.py
- scripts\map_root_project.py
- scripts\master_system_mapper.py
- scripts\query_civic_graph.py
- scripts\query_connections.py
- scripts\query_influence.py
- scripts\repair_future_imports.py
- scripts\system_mapper.py
- scripts\upgrade_editor_dashboard_architecture.py
- scripts\validate_repo.py
- scripts\watch_content.py

## Export Targets

- exports/analytics
- exports/articulate
- exports/book
- exports/civic_intelligence
- exports/civic_intelligence_map
- exports/course
- exports/course_engine
- exports/course_factory
- exports/credentials
- exports/graph_expansion
- exports/graph_persistence
- exports/identity
- exports/knowledge_graph
- exports/learning_runtime
- exports/lesson_player
- exports/mentor
- exports/progress_registry
- exports/project_map
- exports/reader_site
- exports/repo_audit
- exports/system_map
- exports/tracks
- exports/web

## Dashboard Files

- apps\editor-dashboard\app.js
- apps\editor-dashboard\autonomous-course-panel.html
- apps\editor-dashboard\civic-intelligence-dashboard.css
- apps\editor-dashboard\civic-intelligence-dashboard.html
- apps\editor-dashboard\civic-intelligence-dashboard.js
- apps\editor-dashboard\civic-intelligence-map.js
- apps\editor-dashboard\content-manifest.json
- apps\editor-dashboard\course-engine-viewer.js
- apps\editor-dashboard\generate-course.js
- apps\editor-dashboard\index.html
- apps\editor-dashboard\knowledge-graph-viewer.js
- apps\editor-dashboard\learning-runtime-viewer.js
- apps\editor-dashboard\lesson-player.js
- apps\editor-dashboard\README.md
- apps\editor-dashboard\styles.css
- apps\editor-dashboard\track-engine-viewer.js
- apps\editor-dashboard\functions\chapter-context.js
- apps\editor-dashboard\functions\commit-universal.js
- apps\editor-dashboard\functions\export-rise.js
- apps\editor-dashboard\functions\openai-proxy.js
... (1173 total files)