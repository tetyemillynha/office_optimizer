import pygame

class Simulator:
    def __init__(self, visualizer, genetic):
        self.visualizer = visualizer
        self.genetic = genetic
        self.running = True
        self.paused = False
        self.show_info = True

    def run(self):
        """Loop principal com tratamento de erros robusto"""
        try:
            clock = pygame.time.Clock()
            self.genetic.last_improvement = 0

            while self.running:
                # 1. Processa eventos
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        self._handle_key_event(event)

                # 2. Atualização da simulação
                if not self.paused:
                    stop_reason = self.genetic.next_generation()

                    # Sincroniza o estado com o visualizador
                    self.visualizer.best_individual = self.genetic.best_individual
                    self.visualizer.best_fitness = self.genetic.best_fitness
                    self.visualizer.generation = self.genetic.generation

                    if stop_reason:
                        print(f"PARANDO: {stop_reason}")
                        self._handle_stop_condition(stop_reason)
                        self.genetic.save_fitness_plot()
                        break


                # 3. Renderização
                self.visualizer.draw()
                pygame.display.flip()
                clock.tick(10)

        except Exception as e:
            print(f"ERRO: {str(e)}")
        finally:
            pygame.quit()

    def _handle_key_event(self, event):
        """Gerencia eventos de teclado"""
        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_SPACE:
            self.paused = not self.paused
        elif event.key == pygame.K_r:
            self._reset_simulation()
        elif event.key == pygame.K_i:
            self.show_info = not self.show_info
            self.visualizer.show_info = self.show_info

    def _handle_stop_condition(self, stop_reason):
        """Mostra mensagem final e prepara para encerrar"""
        self.visualizer.draw()
        self.draw_final_message(stop_reason)
        pygame.display.flip()
        pygame.time.wait(3000)

    def _reset_simulation(self):
        """Reinicia completamente a simulação"""
        self.genetic.population = [
            self.genetic.create_individual() for _ in range(self.genetic.population_size)
        ]
        self.genetic.generation = 0
        self.genetic.best_fitness = -float('inf')
        self.genetic.best_individual = None
        self.genetic.last_improvement = 0

    def draw_final_message(self, message):
        """Mostra mensagem quando o algoritmo termina"""
        overlay = pygame.Surface((self.visualizer.width, self.visualizer.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))

        text = self.visualizer.big_font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.visualizer.width // 2, self.visualizer.height // 2))

        self.visualizer.screen.blit(overlay, (0, 0))
        self.visualizer.screen.blit(text, text_rect)
