from modulos.empleados.views.lista_empleados import EmpleadosView


class EmpleadosController:
    def get_view(self) -> EmpleadosView:
        return EmpleadosView()
