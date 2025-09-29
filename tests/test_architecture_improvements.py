"""
Testes para as melhorias de arquitetura implementadas na função lifespan.

Testa:
- Separação de responsabilidades
- Tratamento de erros (fail-fast/graceful degradation)
- Scheduler adaptativo
- Cleanup gracioso
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from resync.main import (
    get_auditor_job_config,
    initialize_core_systems,
    initialize_schedulers,
    shutdown_application,
    start_background_services,
    start_monitoring_system,
)


class TestCoreSystemsInitialization:
    """Testes para initialize_core_systems() - fail-fast behavior."""

    @pytest.mark.asyncio
    async def test_initialize_core_systems_success(self):
        """Testa inicialização bem-sucedida de todos os sistemas."""
        with patch("resync.main.agent_manager") as mock_agent_manager:
            mock_agent_manager.load_agents_from_config = AsyncMock()
            mock_agent_manager._get_tws_client = AsyncMock()

            # Should not raise any exception
            await initialize_core_systems()

            # Verify all critical systems were initialized
            mock_agent_manager.load_agents_from_config.assert_called_once()
            mock_agent_manager._get_tws_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_core_systems_agent_manager_failure(self):
        """Testa fail-fast quando Agent Manager falha."""
        with patch("resync.main.agent_manager") as mock_agent_manager:
            mock_agent_manager.load_agents_from_config = AsyncMock(
                side_effect=Exception("Agent config error")
            )

            # Should raise SystemExit
            with pytest.raises(SystemExit) as exc_info:
                await initialize_core_systems()

            assert "Agent Manager initialization failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_initialize_core_systems_tws_client_failure(self):
        """Testa fail-fast quando TWS Client falha."""
        with patch("resync.main.agent_manager") as mock_agent_manager:
            mock_agent_manager.load_agents_from_config = AsyncMock()
            mock_agent_manager._get_tws_client = AsyncMock(
                side_effect=Exception("TWS connection error")
            )

            # Should raise SystemExit
            with pytest.raises(SystemExit) as exc_info:
                await initialize_core_systems()

            assert "TWS Client initialization failed" in str(exc_info.value)


class TestBackgroundServices:
    """Testes para start_background_services() - graceful degradation."""

    @pytest.mark.asyncio
    async def test_start_background_services_success(self):
        """Testa inicialização bem-sucedida dos serviços em background."""
        with patch("resync.main.watch_config_changes") as mock_config_watcher, \
             patch("resync.main.watch_rag_directory") as mock_rag_watcher:

            mock_config_watcher = AsyncMock()
            mock_rag_watcher = AsyncMock()

            tasks = await start_background_services()

            # Should return dictionary with tasks
            assert isinstance(tasks, dict)
            assert "config_watcher" in tasks
            assert "rag_watcher" in tasks

    @pytest.mark.asyncio
    async def test_start_background_services_config_watcher_success(self):
        """Testa que config watcher é iniciado com sucesso."""
        with patch("resync.main.watch_config_changes") as mock_config_watcher:
            mock_config_watcher = AsyncMock()

            tasks = await start_background_services()

            # Config watcher should be created
            assert "config_watcher" in tasks
            assert isinstance(tasks["config_watcher"], asyncio.Task)

    @pytest.mark.asyncio
    async def test_start_background_services_rag_watcher_failure(self):
        """Testa graceful degradation quando RAG watcher falha."""
        with patch("resync.main.watch_config_changes") as mock_config_watcher, \
             patch("resync.main.watch_rag_directory") as mock_rag_watcher:

            mock_config_watcher = AsyncMock()
            # Make the function itself fail when called
            mock_rag_watcher.side_effect = Exception("RAG watcher error")

            # Should still work but log warning (RAG watcher is optional)
            tasks = await start_background_services()

            # Config watcher should still be created (it's critical)
            assert "config_watcher" in tasks
            # RAG watcher should not be created due to failure
            assert "rag_watcher" not in tasks


class TestSchedulerInitialization:
    """Testes para initialize_schedulers() - configuração adaptativa."""

    @pytest.mark.asyncio
    async def test_scheduler_production_config(self):
        """Testa configuração de scheduler para ambiente de produção."""
        with patch("resync.main.settings") as mock_settings, \
             patch("resync.main.AsyncIOScheduler") as mock_scheduler_class:

            mock_settings.APP_ENV = "production"
            mock_settings.IA_AUDITOR_FREQUENCY_HOURS = 6
            mock_settings.IA_AUDITOR_STARTUP_ENABLED = False

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            scheduler = await initialize_schedulers()

            # Verify scheduler was created and configured
            mock_scheduler_class.assert_called_once()
            mock_scheduler.add_job.assert_called_once()
            mock_scheduler.start.assert_called_once()

            # Verify production configuration (6h interval)
            call_args = mock_scheduler.add_job.call_args
            assert call_args[0][1] == "cron"  # type (second positional arg)
            assert "hour" in call_args[1]  # config contains hour (keyword args)

    @pytest.mark.asyncio
    async def test_scheduler_development_config(self):
        """Testa configuração de scheduler para ambiente de desenvolvimento."""
        with patch("resync.main.settings") as mock_settings, \
             patch("resync.main.AsyncIOScheduler") as mock_scheduler_class:

            mock_settings.APP_ENV = "development"

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            scheduler = await initialize_schedulers()

            # Verify development configuration (30min interval)
            call_args = mock_scheduler.add_job.call_args
            assert call_args[0][1] == "interval"  # type (second positional arg)
            assert "minutes" in call_args[1]  # config contains minutes (keyword args)

    @pytest.mark.asyncio
    async def test_scheduler_default_config(self):
        """Testa configuração padrão de scheduler."""
        with patch("resync.main.settings") as mock_settings, \
             patch("resync.main.AsyncIOScheduler") as mock_scheduler_class:

            mock_settings.APP_ENV = "staging"

            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler

            scheduler = await initialize_schedulers()

            # Verify default configuration (6h cron)
            call_args = mock_scheduler.add_job.call_args
            assert call_args[0][1] == "cron"  # type (second positional arg)
            assert "hour" in call_args[1]  # config contains hour (keyword args)

    @pytest.mark.asyncio
    async def test_scheduler_initialization_failure(self):
        """Testa fail-fast quando scheduler falha."""
        with patch("resync.main.AsyncIOScheduler") as mock_scheduler_class:
            mock_scheduler_class.side_effect = Exception("Scheduler error")

            with pytest.raises(SystemExit) as exc_info:
                await initialize_schedulers()

            assert "Scheduler initialization failed" in str(exc_info.value)


class TestMonitoringSystem:
    """Testes para start_monitoring_system() - graceful degradation."""

    @pytest.mark.asyncio
    async def test_monitoring_system_success(self):
        """Testa inicialização bem-sucedida do sistema de monitoring."""
        with patch("resync.main.tws_monitor") as mock_monitor:
            mock_monitor.start_monitoring = AsyncMock()

            await start_monitoring_system()

            mock_monitor.start_monitoring.assert_called_once()

    @pytest.mark.asyncio
    async def test_monitoring_system_failure(self):
        """Testa graceful degradation quando monitoring falha."""
        with patch("resync.main.tws_monitor") as mock_monitor:
            mock_monitor.start_monitoring = AsyncMock(
                side_effect=Exception("Monitoring error")
            )

            # Should not raise exception (monitoring is optional)
            await start_monitoring_system()

            # But should log the error
            mock_monitor.start_monitoring.assert_called_once()


class TestShutdownApplication:
    """Testes para shutdown_application() - cleanup gracioso."""

    @pytest.mark.asyncio
    async def test_shutdown_application_success(self):
        """Testa shutdown gracioso de todos os componentes."""
        with patch("resync.main.tws_monitor") as mock_monitor, \
             patch("resync.main.app") as mock_app:

            # Mock background tasks
            mock_task1 = AsyncMock()
            mock_task2 = AsyncMock()
            background_tasks = {
                "service1": mock_task1,
                "service2": mock_task2
            }

            # Mock scheduler
            mock_app.state.scheduler = MagicMock()
            mock_app.state.scheduler.shutdown = MagicMock()

            # Mock agent manager
            with patch("resync.main.agent_manager") as mock_agent_manager:
                mock_agent_manager.tws_client = MagicMock()
                mock_agent_manager.tws_client.close = AsyncMock()

                await shutdown_application(background_tasks)

                # Verify all cleanup happened
                mock_task1.cancel.assert_called_once()
                mock_task2.cancel.assert_called_once()
                mock_monitor.stop_monitoring.assert_called_once()
                mock_app.state.scheduler.shutdown.assert_called_once()
                mock_agent_manager.tws_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_application_partial_failure(self):
        """Testa shutdown mesmo com algumas falhas."""
        with patch("resync.main.tws_monitor") as mock_monitor, \
             patch("resync.main.app") as mock_app:

            # Mock one task that fails
            mock_task1 = AsyncMock()
            mock_task1.cancel.side_effect = Exception("Task cancel error")
            mock_task2 = AsyncMock()

            background_tasks = {
                "service1": mock_task1,
                "service2": mock_task2
            }

            mock_app.state.scheduler = MagicMock()
            mock_app.state.scheduler.shutdown = MagicMock()

            # Should still complete shutdown despite partial failures
            await shutdown_application(background_tasks)

            # Failed task should still be attempted
            mock_task1.cancel.assert_called_once()
            mock_task2.cancel.assert_called_once()


class TestAuditorJobConfig:
    """Testes para get_auditor_job_config() - configuração adaptativa."""

    def test_production_config(self):
        """Testa configuração de produção."""
        with patch("resync.main.settings") as mock_settings:
            mock_settings.APP_ENV = "production"
            mock_settings.IA_AUDITOR_FREQUENCY_HOURS = 8
            mock_settings.IA_AUDITOR_STARTUP_ENABLED = False

            config = get_auditor_job_config()

            assert config["type"] == "cron"
            assert "hour" in config["config"]
            assert config["startup_enabled"] is False

    def test_development_config(self):
        """Testa configuração de desenvolvimento."""
        with patch("resync.main.settings") as mock_settings:
            mock_settings.APP_ENV = "development"

            config = get_auditor_job_config()

            assert config["type"] == "interval"
            assert "minutes" in config["config"]
            assert config["startup_enabled"] is True

    def test_default_config(self):
        """Testa configuração padrão."""
        with patch("resync.main.settings") as mock_settings:
            mock_settings.APP_ENV = "staging"

            config = get_auditor_job_config()

            assert config["type"] == "cron"
            assert "hour" in config["config"]
            assert config["startup_enabled"] is True


class TestIntegrationWithFastAPI:
    """Testes de integração com FastAPI lifecycle."""

    @pytest.mark.asyncio
    async def test_fastapi_lifespan_integration(self):
        """Testa integração completa com FastAPI lifespan."""
        from fastapi import FastAPI
        from resync.main import lifespan

        app = FastAPI(lifespan=lifespan)

        # Test that lifespan function is properly configured
        assert hasattr(app, "router")
        # FastAPI stores lifespan in a private attribute
        assert hasattr(app, "_lifespan") or hasattr(app, "lifespan")

        # The lifespan function should be callable
        lifespan_context = lifespan(app)
        assert hasattr(lifespan_context, "__aenter__")
        assert hasattr(lifespan_context, "__aexit__")


class TestPerformanceMetrics:
    """Testes de performance e memory usage."""

    @pytest.mark.asyncio
    async def test_startup_performance(self):
        """Testa performance de startup."""
        import time

        start_time = time.time()

        with patch("resync.main.agent_manager") as mock_agent_manager, \
             patch("resync.main.tws_monitor") as mock_monitor, \
             patch("resync.main.settings") as mock_settings:

            # Mock settings to avoid AttributeError
            mock_settings.APP_ENV = "development"
            mock_settings.IA_AUDITOR_FREQUENCY_HOURS = 6
            mock_settings.IA_AUDITOR_STARTUP_ENABLED = True

            mock_agent_manager.load_agents_from_config = AsyncMock()
            mock_agent_manager._get_tws_client = AsyncMock()
            mock_monitor.start_monitoring = AsyncMock()

            # Initialize systems
            await initialize_core_systems()
            background_tasks = await start_background_services()
            scheduler = await initialize_schedulers()
            await start_monitoring_system()

            # Cleanup
            await shutdown_application(background_tasks)

            end_time = time.time()
            duration = end_time - start_time

            # Startup should be fast (< 5s for tests)
            assert duration < 5.0, f"Startup took {duration:.2f}s, should be < 5s"

    @pytest.mark.asyncio
    async def test_memory_usage_during_lifecycle(self):
        """Testa memory usage durante o lifecycle."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        with patch("resync.main.agent_manager") as mock_agent_manager, \
             patch("resync.main.tws_monitor") as mock_monitor, \
             patch("resync.main.settings") as mock_settings:

            # Mock settings to avoid AttributeError
            mock_settings.APP_ENV = "development"
            mock_settings.IA_AUDITOR_FREQUENCY_HOURS = 6
            mock_settings.IA_AUDITOR_STARTUP_ENABLED = True

            mock_agent_manager.load_agents_from_config = AsyncMock()
            mock_agent_manager._get_tws_client = AsyncMock()
            mock_monitor.start_monitoring = AsyncMock()

            # Run full lifecycle
            await initialize_core_systems()
            background_tasks = await start_background_services()
            scheduler = await initialize_schedulers()
            await start_monitoring_system()
            await shutdown_application(background_tasks)

            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            # Memory increase should be reasonable (< 50MB for tests)
            assert memory_increase < 50, f"Memory increase: {memory_increase:.1f}MB, should be < 50MB"

    @pytest.mark.asyncio
    async def test_concurrent_access_during_shutdown(self):
        """Testa acesso concorrente durante shutdown."""
        with patch("resync.main.tws_monitor") as mock_monitor, \
             patch("resync.main.app") as mock_app:

            mock_monitor.stop_monitoring = AsyncMock()
            mock_app.state.scheduler = MagicMock()
            mock_app.state.scheduler.shutdown = MagicMock()

            # Mock background tasks
            background_tasks = {
                "service1": AsyncMock(),
                "service2": AsyncMock(),
            }

            # Run shutdown in background
            shutdown_task = asyncio.create_task(
                shutdown_application(background_tasks)
            )

            # Try to access components during shutdown
            # This should not cause race conditions or deadlocks
            await asyncio.sleep(0.1)  # Small delay

            # Shutdown should complete successfully
            await shutdown_task
