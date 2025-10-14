Foram identificadas 94 funções com complexidade C e D no projeto Python, sendo:

- 5 funções com complexidade D (alta complexidade):
  1. resync\core\async_cache.py: set (D, 25)
  2. resync\core\tws_monitor.py: get_performance_report (D, 23)
  3. resync\core\async_cache.py: rollback_transaction (D, 22)
  4. resync\core\audit_db.py: _validate_audit_record (D, 22)
  5. resync\core\soc2_compliance.py: generate_compliance_report (D, 22)

- 89 funções com complexidade C (moderada a alta complexidade), incluindo:
  - resync\core\utils\llm.py: call_llm (C, 20)
  - resync\core\async_cache.py: get (C, 20)
  - resync\core\async_cache.py: __init__ (C, 20)
  - resync\core\utils\json_parser.py: parse_llm_json_response (C, 17)
  - resync\services\tws_service.py: get_job_history (C, 17)
  - resync\tool_definitions\tws_tools.py: analyze_failures (C, 15)
  - resync\core\service_discovery.py: _select_instance (C, 14)
  - resync\core\utils\error_utils.py: create_error_response_from_exception (C, 14)
  - resync\core\siem_integrator.py: _initialize_rules (C, 12)
  - resync\core\sql_preparer.py: get_or_prepare (C, 11)

As funções com complexidade D são as mais críticas e devem ser priorizadas para refatoração, seguidas pelas funções com complexidade C que têm maior impacto no sistema. As funções identificadas serão refatoradas utilizando padrões de projeto como Strategy, Factory e Command, conforme planejado anteriormente.