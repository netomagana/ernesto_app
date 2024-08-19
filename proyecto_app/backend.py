from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/ernesto_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definición del modelo de datos
class RegisterClient(db.Model):
    __tablename__ = 'register_client'  # Nombre de la tabla en la base de datos
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    vehiculo = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    delete_flag = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'vehiculo': self.vehiculo,
            'modelo': self.modelo,
            'fecha': self.fecha.isoformat(),  # Convertir fecha a formato ISO
            'delete_flag': self.delete_flag
        }

# Crear las tablas en la base de datos
@app.before_first_request
def create_tables():
    db.create_all()

# Endpoint GET para obtener todos los registros
@app.route('/register_clients', methods=['GET'])
def get_register_clients():
    register_clients = RegisterClient.query.filter_by(delete_flag=False).all()
    return jsonify([r.to_dict() for r in register_clients])

# Endpoint GET para obtener un registro por ID
@app.route('/register_clients/<int:id>', methods=['GET'])
def get_register_client(id):
    register_client = RegisterClient.query.filter_by(id=id, delete_flag=False).first()
    if register_client is None:
        abort(404, description="Registro no encontrado")
    return jsonify(register_client.to_dict())

# Endpoint POST para crear un nuevo registro
@app.route('/register_clients', methods=['POST'])
def create_register_client():
    data = request.get_json()
    if not all(key in data for key in ('nombre', 'vehiculo', 'modelo', 'fecha')):
        abort(400, description="Datos incompletos")
    try:
        nuevo_register_client = RegisterClient(
            nombre=data['nombre'],
            vehiculo=data['vehiculo'],
            modelo=data['modelo'],
            fecha=data['fecha']
        )
        db.session.add(nuevo_register_client)
        db.session.commit()
        return jsonify(nuevo_register_client.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        abort(400, description="Error en los datos proporcionados")

# Endpoint PUT para actualizar un registro
@app.route('/register_clients/<int:id>', methods=['PUT'])
def update_register_client(id):
    data = request.get_json()
    register_client = RegisterClient.query.filter_by(id=id, delete_flag=False).first()
    if register_client is None:
        abort(404, description="Registro no encontrado")
    
    if 'nombre' in data:
        register_client.nombre = data['nombre']
    if 'vehiculo' in data:
        register_client.vehiculo = data['vehiculo']
    if 'modelo' in data:
        register_client.modelo = data['modelo']
    if 'fecha' in data:
        register_client.fecha = data['fecha']

    db.session.commit()
    return jsonify(register_client.to_dict())

# Endpoint DELETE para marcar un registro como eliminado
@app.route('/register_clients/<int:id>', methods=['DELETE'])
def delete_register_client(id):
    register_client = RegisterClient.query.filter_by(id=id).first()
    if register_client is None:
        abort(404, description="Registro no encontrado")
    
    register_client.delete_flag = True
    db.session.commit()
    return jsonify({'message': 'Registro marcado como eliminado'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
