from supabase import create_client
import bcrypt

class Mensajes:
    def __init__(self):
        self.Exito = {
            "Conexion":"✅ Conexión exitosa",
            "Consulta":"✅ Consulta exitosa"
            }
        self.Fallo = {
            "Consulta":"⚠️ Conectado, pero la consulta falló: "
        }
        self.Error = {
            "Conexion":"❌ Error al conectar, verifique la conexión",
            "Consulta":"❌ Error al hacer la consulta: ",
            "Crud-Consulta":"❌ Error al intentar hacer la consulta: ",
            "Crud-Error":"❌ Error interno en el crud"
        }
        self.Usuarios = {
            "Existe-Nombre":"⚠️ Ya existe un usuario registrado con este nombre",
            "Existe-Correo":"⚠️ Ya existe un usuario registrado con este correo",
            "Registrado":"✅ Usuario registrado",
            "Actualizado":"✅ Usuario actualizado",
            "Eliminado":"🗑️ Usuario eliminado correctamente",
            "Autenticado":"✅ Usuario autenticado",
            "No-Autenticado":"❌ Usuario no autenticado / Usuario no existe"
        }
        self.Pacientes = {
            "Existe-Nombre":"⚠️ Ya existe un paciente registrado con este nombre",
            "Existe-Correo":"⚠️ Ya existe un paciente registrado con este correo",
            "No_existe":"❌ No existe ningún paciente registrado con este nombre",
            "Registrado":"✅ Paciente registrado",
            "Actualizado":"✅ Paciene actualizado",
            "No-Encontrado":"❌ No se encontró este paciente paciente"
        }
        self.Medicamentos ={
            "Registrado":"💊 Medicamento registrado",
            "Existe":"⚠️ Ya existe un medicamento registrado con los mismos datos",
            "Actualizado":"✅ Paciene actualizado",
            "Eliminado":"🗑️ Medicamento eliminado correctamente",
            "Error":"❌ Error al intentar obtener los medicamentos"
        }
        self.Tomas = {
            "Registrado": "💊 Registro de toma de medicamento creado correctamente",
            "Existe":"⚠️ Ya existe un medicamento registrado para esta fecha y hora hora",
            "Actualizado": "🔄 Registro de toma de medicamento actualizado",
            "Eliminado": "🗑️ Registro de toma de medicamento eliminado",
            "Error":"❌ Error al intentar registrar la toma de medicamentos"
        }
        self.Signos = {
            "Registrado": "✅ Signo vital registrado correctamente",
            "Eliminado": "🗑️ Signo vital eliminado correctamente",
            "Existe": "⚠️ Ya se registró este signo vital con los mismos datos",
            "No-Encontrado": "⚠️ No se encontraron signos vitales de para este paciente"
        }
        self.Citas = {
            "Registrado": "✅ Cita médica registrada correctamente",
            "Actualizado": "✏️ Cita médica actualizada exitosamente.",
            "Eliminado": "🗑️ La cita médica fue eliminada con éxito.",
            "Existe": "⚠️ Ya existe una cita médica registrada para la misma fecha y hora.",
            "Existe-Cita": "⚠️ Ya existe una cita médica registrada para este paciente en la misma fecha y hora.",
            "No-encontrado": "❌ No se encontró ninguna cita médica con los datos proporcionados.",
            "No-Guardada":"❌ No fue posible guardar la cita, cita y tomas no registrados",
            "Id-No-Obtenida":"❌ No fue posible obtener el Id de esta cita"
        }
        self.Doctores = {
            "No-Encontrado":"❌ No se encontró el doctor"
        }


    def Coincidencias(self, tabla="", campo="el campo", valor="valor", coincide=True):
        if coincide:
            return f"✅ La tabla {tabla} tiene al menos un registro donde {campo} = {valor}."
        else:
            return f"❌ No se encontró ningún registro en {tabla} donde {campo} = {valor}."

class Conexiones:
    def __init__(self):
        self.url=""
        self.key=""
        self.supabase = create_client(self.url, self.key)
        self.msg = Mensajes()

    def Probar_Conexion(self, tabla_de_prueba="usuarios"):
        try:
            response = self.supabase.table(tabla_de_prueba).select("*").limit(1).execute()
            if response.status_code == 200:
                print(self.msg.Exito["Conexion"])
                return True
            else:
                print(self.msg.Fallo["Consulta"] + f"{response.status_code}")
                return False
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return False

class Consultas:
    def __init__(self):
        conexion = Conexiones()
        self.supabase = conexion.supabase
        self.msg = Mensajes()

# ------------------------------------------ [ Generales ] --------------------------------------------------------------------------


    def existe_valor(self, tabla, campo, valor):
        m = self.msg
        try:
            resultado = (
                self.supabase.table(tabla)
                .select(campo)
                .eq(campo, valor)
                .limit(1)
                .execute()
            )

            resultado_dict = resultado.model_dump()

            if "error" in resultado_dict and resultado_dict["error"] is not None:
                print(m.Error["Consulta"], resultado_dict["error"])
                return None

            print(m.Exito["Consulta"])

            datos = resultado_dict.get("data", [])
            if datos:
                print(m.Coincidencias(tabla, campo, valor, True))
                return True
            else:
                print(m.Coincidencias(tabla, campo, valor, False))
                return False

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None


    def ejecutar(self, consulta):
        try:
            resultado = consulta.execute()

            # Esto convierte a dict y permite acceder al posible error
            resultado_dict = resultado.model_dump()

            if "error" in resultado_dict and resultado_dict["error"] is not None:
                print(self.msg.Error["Consulta"], resultado_dict["error"])
                return None

            print(self.msg.Exito["Consulta"])
            return resultado
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

    
#    def obtener_mensaje(self, tipo):
#        mensajes_tabla = getattr(self.msg, tipo, None)
#        return mensajes_tabla

    def comprobar_nombre_correo(self, tabla, nombre, correo):
        
        mensaje = getattr(self.msg, tabla.capitalize(), None)
        if not mensaje:
            print(f"⚠️ No hay mensajes definidos para {tabla}")
            
        if self.existe_valor(tabla, "nombre", nombre):
            print(mensaje["Existe-Nombre"])
            return True

        if self.existe_valor(tabla, "correo_electronico", correo):
            print(mensaje["Existe-Correo"])
            return True

        return False

    def validar_cita(self, fecha, hora, paciente_id):
        try:
            consulta = (
                self.supabase.table("citas")
                .select("id")
                .match({
                    "fecha": fecha,
                    "hora": hora,
                    "paciente_id": paciente_id
                })
                .limit(1)
            )
            resultado = self.ejecutar(consulta)
            if resultado and resultado.data:
                return True  # ✅ Ya existe la cita
            return False  # ❌ No existe
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return True

    def validar_toma_medicamento(self, cita_id, medicamento_id, fecha, hora):
        try:
            consulta = (
                self.supabase.table("tomasmedicamentos")
                .select("id")
                .match({
                    "cita_id": cita_id,
                    "medicamento_id": medicamento_id,
                    "fecha": fecha,
                    "hora": hora
                })
                .limit(1)
                .execute()
            )
            resultado_dict = consulta.model_dump()

            if resultado_dict.get("error"):
                print(f"❌ Error en validación de toma: {resultado_dict['error']}")
                return None

            datos = resultado_dict.get("data", [])
            if datos:
                print(self.msg.Tomas["Existe"])
                return True  # Ya existe
            return False  # No existe

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

#-------------------------------------------------------------------------------------------------------------------------------


# ------------------------------------------ [ Usuarios ] ----------------------------------------------------------------------


    def autenticar_usuario(self, correo: str, contraseña_input: str):
        try:
            consulta = self.supabase.table("usuarios").select("id, nombre, correo, contraseña_hash").eq("correo", correo).limit(1)
            resultado = self.ejecutar(consulta)

            if resultado and resultado.data:
                usuario = resultado.data[0]
                #print("Resultado consulta:", resultado.data)

                if bcrypt.checkpw(contraseña_input.encode('utf-8'), usuario['contraseña_hash'].encode('utf-8')):
                    print(self.msg.Usuarios["Autenticado"])
                    return usuario  # Devuelve datos del usuario autenticado
                else:
                    print(self.msg.Usuarios["No-Autenticado"])
                    return None
            else:
                print(self.msg.Usuarios["No-Autenticado"])
                return None
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None


    def Crear_usuario(self, nombre, correo, contraseña_hash, rol="paciente"):

        if self.comprobar_nombre_correo("usuarios",nombre,correo):
            return None
        
        try:
    
            # Hash de la contraseña con salt
            contraseña_crypt = bcrypt.hashpw(contraseña_hash.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            consulta = self.supabase.table("usuarios").insert(
                {
                "nombre": nombre,
                "correo": correo,
                "contraseña_hash": contraseña_crypt,
                "rol": rol
                }
            )

            resultado = self.ejecutar(consulta)
            if resultado:
                print(self.msg.Usuarios["Registrado"])
                return True
            
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

    def Obtener_usuarios(self):
        consulta = self.supabase.table("usuarios").select("id, nombre, correo")

        try:

            resultado = self.ejecutar(consulta)
            if resultado:
                return resultado.data
            
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None
        return None

    def Actualizar_usuario(self, user_id, datos: dict):
        #Verificar si existe el usuario
        if not self.existe_valor("usuarios", "id", user_id):
            print(self.msg.Coincidencias("","id", f"{user_id}", False))
            return None

        try:

            consulta = self.supabase.table("usuarios").update(datos).eq("id", user_id)
            resultado = self.ejecutar(consulta)
            if resultado:
                print(self.msg.Usuarios["Actualizado"])
                return True
            
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

    def Eliminar_usuario(self, user_id):
        #Verificar si existe el usuario
        if not self.existe_valor("usuarios", "id", user_id):
            print(self.msg.Coincidencias("","id", f"{user_id}",False))
            return None
        
        try:

            consulta = self.supabase.table("usuarios").delete().eq("id", user_id)
            resultado = self.ejecutar(consulta)
            if resultado:
                print(self.msg.Usuarios["Eliminado"])
                return True
            
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None    
# -----------------------------------------------------------------------------------------------------------------------------------



# ------------------------------------------ [ Pacientes ] --------------------------------------------------------------------------

    def crear_paciente(self, nombre, telefono, domicilio, correo_electronico, doctor_id):

        if self.comprobar_nombre_correo("pacientes", nombre, correo_electronico):
            return None

        try:

            datos = {
                "nombre": nombre,
                "telefono": telefono,
                "domicilio": domicilio,
                "correo_electronico": correo_electronico,
                "doctor_id": doctor_id
            }

            consulta = self.supabase.table("pacientes").insert(datos)

            if not self.ejecutar(consulta):
                return False
            
            print(self.msg.Pacientes["Registrado"])
            return True
        
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

    def obtener_pacientes_por_doctor(self, doctor_id, cantidad = False):

        try:

            if cantidad:
                consulta = self.supabase.table("pacientes").select("id", count="exact").eq("doctor_id", doctor_id)
                resultado = self.ejecutar(consulta)
                return resultado.count if resultado else 0
            else:
                consulta = (
                    self.supabase.table("pacientes")
                    .select("id, nombre, telefono, domicilio, correo_electronico")
                    .eq("doctor_id", doctor_id)
                )


            resultado = self.ejecutar(consulta)
            if resultado:
                return resultado.data
            
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None
        return None

    def actualizar_paciente(self, id, datos: dict):
        #Verificar si existe el usuario
        if not self.existe_valor("pacientes", "id", id):
            print(self.msg.Coincidencias("","id", f"{id}", False))
            return None

        try:

            consulta = self.supabase.table("pacientes").update(datos).eq("id", id)
            resultado = self.ejecutar(consulta)
            if resultado:
                print(self.msg.Usuarios["Actualizado"])
                return True
            return False
            
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

    def eliminar_paciente(self, id):
        #Verificar si existe el usuario
        if not self.existe_valor("pacientes", "id", id):
            print(self.msg.Coincidencias("","id", f"{id}",False))
            return None
        
        try:

            consulta = self.supabase.table("pacientes").delete().eq("id", id)
            resultado = self.ejecutar(consulta)
            if resultado:
                print(self.msg.Usuarios["Eliminado"])
                return True
            return False
            
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None   

# -----------------------------------------------------------------------------------------------------------------------------------




# ------------------------------------------ [ Medicamentos ] ----------------------------------------------------------------------

    def crear_medicamento(self, nombre, ingrediente_activo, fecha_caducidad):
        # Validar duplicados
        def validar_medicamentos():
            valores = {
                "nombre": False,
                "ingrediente":False,
                "fecha":False
            }

            if self.existe_valor("medicamentos","nombre", nombre):
                valores["nombre"] = True
                
            if self.existe_valor("medicamentos","ingrediente_activo", ingrediente_activo):
                valores["ingrediente"] = True
                
#            if self.existe_valor("Medicamentos","fecha_caducidad", fecha_caducidad):
#                valores["fecha"] = True

            if all(valores.values()):
                return True
            return False
            

        try:

            if validar_medicamentos():
                print(self.msg.Medicamentos["Existe"])
                return False

            datos = {
                "nombre": nombre,
                "ingrediente_activo": ingrediente_activo,
                "fecha_caducidad": fecha_caducidad
            }

            consulta = self.supabase.table("medicamentos").insert(datos)

            if not self.ejecutar(consulta):
                return False

            print(self.msg.Medicamentos["Registrado"])
            return True

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

    def obtener_medicamentos(self, cantidad = False):

        try:

            if cantidad:
                consulta = self.supabase.table("medicamentos").select("id", count="exact")
                resultado = self.ejecutar(consulta)
                return resultado.count if resultado else 0
            else:
                consulta = self.supabase.table("medicamentos").select("id, nombre, ingrediente_activo, fecha_caducidad")

            resultado = self.ejecutar(consulta)
            if resultado:
                return resultado.data
            

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

    def actualizar_medicamento(self, id, datos: dict):

        try:

            # Verificar si existe el medicamento
            if not self.existe_valor("medicamentos", "id", id):
                print(self.msg.Coincidencias("", "id", f"{id}", False))
                return None

            consulta = self.supabase.table("medicamentos").update(datos).eq("id", id)
            resultado = self.ejecutar(consulta)
            if resultado:
                print(self.msg.Medicamentos["Actualizado"])
                return True
            return False

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

    def eliminar_medicamento(self, id):
        # Verificar si existe el medicamento
        if not self.existe_valor("medicamentos", "id", id):
            print(self.msg.Coincidencias("", "id", f"{id}", False))
            return None

        try:
            consulta = self.supabase.table("medicamentos").delete().eq("id", id)
            resultado = self.ejecutar(consulta)
            if resultado:
                print(self.msg.Medicamentos["Eliminado"])
                return True
            return False

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None
# -----------------------------------------------------------------------------------------------------------------------------------




# ------------------------------------------ [ Tomas de medicamentos ] ------------------------------------------------------------

    def registrar_toma(self, paciente_id, medicamento_id, fecha, hora, confirmacion=False, cita_id=None):
        try:
            datos = {
                "paciente_id": paciente_id,
                "medicamento_id": medicamento_id,
                "fecha": fecha,
                "hora": hora,
                "confirmacion": confirmacion,
                "cita_id": cita_id  # Agregamos la referencia a la cita
            }
            consulta = self.supabase.table("tomasmedicamentos").insert(datos)
            resultado = self.ejecutar(consulta)

            if not resultado.data:
                print(f"Error al registrar toma: {resultado.data}")
                return False

            print(self.msg.Tomas["Registrado"])
            return True

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None


    def obtener_tomas(self, paciente_id=None, usar_vista=False):
        try:
            
            if not paciente_id:

                return False
            
            if usar_vista:
                consulta = self.supabase.table("vista_medicamentos_por_cita").select("*").eq("paciente_id", paciente_id)
            else:
                consulta = self.supabase.table("tomasmedicamentos").select(
                    """
                    paciente_id,
                    pacientes(nombre),
                    medicamento_id,
                    medicamentos(nombre, ingrediente_activo),
                    fecha,
                    hora,
                    confirmacion
                    """
                ).eq("paciente_id", paciente_id)

            resultado = self.ejecutar(consulta)
            if resultado:
                return resultado.data
            
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

    def comfirmar_toma(self, id, confirmacion):

        try:

            # Verificar si existe el medicamento
            if not self.existe_valor("tomasmedicamentos", "id", id):
                print(self.msg.Coincidencias("", "id", f"{id}", False))
                return None

            consulta = self.supabase.table("tomasmedicamentos").update(confirmacion).eq("id", id)
            resultado = self.ejecutar(consulta)
            if resultado:
                print(self.msg.Medicamentos["Actualizado"])
                return True
            return False

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

    def eliminar_toma(self, id):

        try:
            # Verificar si existe el la toma en el registro
            if not self.existe_valor("tomasmedicmentos", "id", id):
                print(self.msg.Coincidencias("", "id", f"{id}", False))
                return None
            
            consulta = self.supabase.table("tomasmedicmentos").delete().eq("id", id)
            resultado = self.ejecutar(consulta)
            if resultado:
                print(self.msg.Medicamentos["Eliminado"])
                return True
            return False

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

# -----------------------------------------------------------------------------------------------------------------------------------




# ------------------------------------------ [ Signos vitales ] -------------------------------------------------------------------


    def registrar_signos(self, paciente_id, tipo, valor, fecha_hora):

        try:

            
            def validar_signo_vital(paciente_id, tipo, valor, fecha_hora):
                valores = {
                    "paciente": False,
                    "tipo": False,
                    "valor": False,
                    "fecha_hora": False
                }

                if self.existe_valor("signosvitales", "paciente_id", paciente_id):
                    valores["paciente"] = True

                if self.existe_valor("signosvitales", "tipo", tipo):
                    valores["tipo"] = True

                if self.existe_valor("signosvitales", "valor", valor):
                    valores["valor"] = True

                if self.existe_valor("signosvitales", "fecha_hora", fecha_hora):
                    valores["fecha_hora"] = True

                # Si todos los campos coinciden, consideramos que ya existe ese registro
                if all(valores.values()):
                    return True
                return False

            if validar_signo_vital(paciente_id, tipo, valor, fecha_hora):
                print(self.msg.Signos["Existe"])
                return False

            datos = {
                "paciente_id": paciente_id,
                "tipo": tipo,
                "valor": valor,
                "fecha_hora": fecha_hora
            }
            consulta = self.supabase.table("signosvitales").insert(datos)

            if not self.ejecutar(consulta):
                return False

            print(self.msg.Signos["Registrado"])
            return True

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

    def obtener_signos(self, paciente_id=None, usar_vista=False):
        try:
            
            if not paciente_id:
                print(self.msg.Signos["No-encontrado"])
                return False
            
            if not self.existe_valor("signosvitales", "paciente_id", paciente_id):
                print(self.msg.Coincidencias("", "id", f"{paciente_id}", False))
                return False

            if usar_vista:
                consulta = self.supabase.table("vista_signos_paciente").select("*").eq("paciente_id", paciente_id)
            else:
                consulta = self.supabase.table("signosvitales").select(
                    """
                    paciente_id,
                    Pacientes(nombre),
                    tipo,
                    valor,
                    fecha_hora
                    """
                ).eq("paciente_id", paciente_id)

            resultado = self.ejecutar(consulta)
            if resultado:
                return resultado.data
            
        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None


    def eliminar_signos(self, id):

        try:
            # Verificar si existe el la toma en el registro
            if not self.existe_valor("signosvitales", "id", id):
                print(self.msg.Coincidencias("", "id", f"{id}", False))
                return None
            
            consulta = self.supabase.table("signosvitales").delete().eq("id", id)
            resultado = self.ejecutar(consulta)
            if resultado:
                print(self.msg.Signos["Eliminado"])
                return True
            return False

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

# -----------------------------------------------------------------------------------------------------------------------------------




# ------------------------------------------ [ Citas médicas ] --------------------------------------------------------------------

    def crear_cita(self, fecha, hora, especialidad, paciente_id, doctor_id, diagnostico=""):
        try:
            # Validar paciente
            if not self.existe_valor("pacientes", "id", paciente_id):
                print(self.msg.Pacientes["No-encontrado"])
                return False

            # Validar doctor con rol médico
            # Obtener nombre del doctor (opcional, si quieres guardar el nombre)
            consulta_doctor = (
                self.supabase.table("usuarios")
                .select("nombre")
                .eq("id", doctor_id)
                .eq("rol", "medico")  # ✅ Validamos que sea médico
                .single()
            )
            
            resultado_doctor = self.ejecutar(consulta_doctor)
            if not resultado_doctor or not resultado_doctor.data:
                print(self.msg.Doctores["No-encontrado"])
                return False
            
            nombre_doctor = resultado_doctor.data["nombre"]

            # Validar si ya hay cita en ese horario para ese paciente
            existe = self.validar_cita(fecha, hora, paciente_id)
            if existe:
                print(self.msg.Citas["Existe-cita"])
                id_cita = self.actualizar_cita(fecha, hora, especialidad, paciente_id, nombre_doctor, diagnostico)
                return id_cita

            datos = {
                "fecha": fecha,
                "hora": hora,
                "especialidad": especialidad,
                "paciente_id": paciente_id,
                "doctor": nombre_doctor,  # O usar doctor_id si cambias el esquema
                "diagnostico": diagnostico
            }

            consulta = self.supabase.table("citas").insert(datos)
            resultado = self.ejecutar(consulta)

            # Dentro de crear_cita
            if resultado.data:
                id_cita = resultado.data[0]["id"]  # ✅ Así accedes al ID
                print(f"Id de la cita: {id_cita}")
                print(self.msg.Citas["Registrado"])
                return id_cita
            

            return False

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None
        
    def crear_cita_y_registrar_toma(self, fecha, hora, especialidad, doctor_id, paciente_id, medicamento_id, fecha_toma, hora_toma, diagnostico="", confirmacion=False):
        try:
            # Validar o crear cita
            if not self.validar_cita(fecha, hora, paciente_id):
                id_cita = self.crear_cita(fecha, hora, especialidad, paciente_id, doctor_id, diagnostico)
                if not id_cita:
                    print(self.msg.Citas["No-Guardada"])
                    return None
            else:
                id_cita = self.actualizar_cita(fecha, hora, especialidad, paciente_id, doctor_id, diagnostico)
                if not id_cita:
                    print(self.msg.Citas["Id-No-Obtenida"])
                    return None
                print(f"La cita tiene el ID: {id_cita}")


            # Validar si ya existe toma del medicamento para esa cita y hora
            existe_toma = self.validar_toma_medicamento(id_cita, medicamento_id, fecha_toma, hora_toma)
            if existe_toma:
                print(self.msg.Tomas["Existe"])
                return False

            # Registrar toma de medicamento
            resultado_toma = self.registrar_toma(paciente_id, medicamento_id, fecha_toma, hora_toma, confirmacion, id_cita)
            if not resultado_toma:
                print(self.msg.Tomas["Error"])
                return False

            print(self.msg.Tomas["Registrado"])
            return True

        except Exception as e:
            print(self.msg.Error["Crud-Error"], e)
            return None

    def obtener_citas(self, paciente_id=None, usar_vista=False):
        try:
            if not paciente_id:
                print(self.msg.Citas["No-encontrado"])
                return False

            if not self.existe_valor("citas", "paciente_id", paciente_id):
                print(self.msg.Coincidencias("", "id", f"{paciente_id}", False))
                return False
            
            if usar_vista:
                consulta = self.supabase.table("vista_citas_paciente").select("*").eq("paciente_id", paciente_id)
            else:
                consulta = self.supabase.table("citas").select(
                    """
                    id,
                    paciente_id,
                    pacientes(nombre),
                    fecha,
                    hora,
                    doctor,
                    especialidad,
                    diagnostico,
                    tomasmedicamentos(
                        medicamento_id,
                        medicamentos(nombre, ingrediente_activo),
                        fecha,
                        hora,
                        confirmacion
                    )
                    """
                ).eq("paciente_id", paciente_id).eq("activo", True)

            resultado = self.ejecutar(consulta)
            if resultado:
                return resultado.data
            return False

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None
        
    def obtener_citas_del_doctor(self, doctor_id, cantidad=False):
        try:
            # Primero obtener el nombre del doctor usando su id
            consulta_doctor = self.supabase.table("usuarios").select("nombre").eq("id", doctor_id).single()
            resultado_doctor = self.ejecutar(consulta_doctor)
            if not resultado_doctor or not resultado_doctor.data:
                print(self.msg.Doctores["No-encontrado"])
                return []

            nombre_doctor = resultado_doctor.data["nombre"]

            if cantidad:
                consulta = self.supabase.table("citas").select("id", count="exact").eq("doctor", nombre_doctor).eq("activo", True)
                resultado = self.ejecutar(consulta)
                return resultado.count if resultado else 0

            else:
                # Filtrar citas usando el nombre del doctor
                consulta = self.supabase.table("citas").select(
                    """
                    id,
                    paciente_id,
                    pacientes(nombre),
                    fecha,
                    hora,
                    doctor,
                    especialidad,
                    diagnostico,
                    tomasmedicamentos(
                        medicamento_id,
                        medicamentos(nombre, ingrediente_activo),
                        fecha,
                        hora,
                        confirmacion
                    )
                    """
                ).eq("doctor", nombre_doctor).eq("activo", True)

            resultado = self.ejecutar(consulta)
            if resultado:
                return resultado.data
            return []

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None

    def actualizar_cita(self, fecha, hora, especialidad, paciente_id, doctor_id, diagnostico=""):
        try:
            print("Entra a actualizar_cita")
            consulta_doctor = (
                self.supabase.table("usuarios")
                .select("nombre")
                .eq("id", doctor_id)
                .eq("rol", "medico")
                .single()
            )
            
            resultado_doctor = self.ejecutar(consulta_doctor)
            if not resultado_doctor or not resultado_doctor.data:
                print(self.msg.Doctores["No-encontrado"])
                return False
            
            nombre_doctor = resultado_doctor.data["nombre"]

            datos = {
                "especialidad": especialidad,
                "doctor": nombre_doctor,
                "diagnostico": diagnostico
            }

            consulta = (
                self.supabase.table("citas")
                .update(datos)
                .eq("paciente_id", paciente_id)
                .eq("fecha", fecha)
                .eq("hora", hora)
            )

            resultado = self.ejecutar(consulta)
            print("Ejecuta el update")
            print(f"Resultado del update: {resultado}")

            # Aquí validamos si la actualización afectó filas
            if resultado and resultado.data:
                print(self.msg.Citas["Actualizado"])
                # Para obtener el id de la cita actualizada, hacemos una consulta aparte
                consulta_cita = (
                    self.supabase.table("citas")
                    .select("id")
                    .eq("paciente_id", paciente_id)
                    .eq("fecha", fecha)
                    .eq("hora", hora)
                    .single()
                )
                resultado_cita = self.ejecutar(consulta_cita)
                print("Ejecuta consulta para obtener id")

                if resultado_cita and resultado_cita.data:
                    id_cita = resultado_cita.data["id"]
                    print(f"Id de la cita actualizada: {id_cita}")
                    return id_cita
                else:
                    print(self.msg.Citas["Actualizado"])
                    return True  # Actualizó pero no pudo obtener id

            print(self.msg.Citas["No-encontrado"])
            return False

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return None
    
    def eliminar_cita(self, cita_id):
        try:
            # 1. Verificar si hay tomas de medicamentos asociadas en la vista
            consulta_vista = (
                self.supabase.table("vista_medicamentos_por_cita")
                .select("cita_id")
                .eq("cita_id", cita_id)
                .limit(1)
            )
            resultado = self.ejecutar(consulta_vista)
            
            datos = []
            if resultado and resultado.data:
                datos = resultado.data

            if datos:
                # 2. Si hay registros, solo actualiza el estado en la tabla citas
                actualizar = (
                    self.supabase.table("citas")
                    .update({"activo": False})
                    .eq("id", cita_id)
                )
                resultado = self.ejecutar(actualizar)
                if resultado:
                    print(self.msg.Citas["Actualizado"])
                    return True
                
            else:
                # 3. Si no hay registros, eliminar completamente la cita
                eliminar = (
                    self.supabase.table("citas")
                    .delete()
                    .eq("id", cita_id)
                )
                resultado = self.ejecutar(eliminar)
                if resultado:
                    print(self.msg.Citas["Eliminado"])
                    return True

            return True

        except Exception as e:
            print(f"{self.msg.Error['Crud-Error']}: {e}")
            return False
