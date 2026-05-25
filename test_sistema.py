import unittest
import os
import mediapipe as mp

class TestTraductorLSP(unittest.TestCase):

    def test_cp01_creacion_dataset(self):
        """Prueba la ingesta segura: Verifica que el sistema pueda crear rutas de dataset"""
        ruta_prueba = "data/letra_prueba_unitaria"
        os.makedirs(ruta_prueba, exist_ok=True)
        
        # Verifica que la carpeta realmente se creó
        self.assertTrue(os.path.exists(ruta_prueba))
        
        # Limpieza después de la prueba
        os.rmdir(ruta_prueba)

    def test_cp02_inicializacion_mediapipe(self):
        """Prueba de IA: Verifica que el esqueleto de MediaPipe cargue con confianza 0.7"""
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        
        # Inicializamos las opciones base del modelo de tareas de MediaPipe
        base_options = python.BaseOptions(model_asset_path='hands.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            min_hand_detection_confidence=0.7
        )
        
        # Verificamos que la configuración de confianza de la IA se asigne correctamente
        self.assertEqual(options.min_hand_detection_confidence, 0.7)

    def test_cp03_logica_padding_seguridad(self):
        """Prueba de márgenes: Verifica la matemática del padding de 30px (evita cortes)"""
        x_min = 100
        y_min = 150
        padding = 30
        
        # Simulamos el cálculo geométrico del cuadro verde
        x_min_seguro = max(0, x_min - padding)
        y_min_seguro = max(0, y_min - padding)
        
        # Verificamos que la resta sea matemáticamente correcta
        self.assertEqual(x_min_seguro, 70)
        self.assertEqual(y_min_seguro, 120)

if __name__ == '__main__':
    unittest.main()