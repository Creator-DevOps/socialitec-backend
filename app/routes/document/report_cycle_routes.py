from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date
from app.utils.auth import jwt_required
from app.services.document.report_cycle_services import (
    format_cycle,
    format_cycle_item,
    get_cycles_paginated,
    get_cycle_by_id,
    create_cycle,
    update_cycle,
    delete_cycle,
    get_cycle_items_paginated,
    get_cycle_item_by_id,
    create_cycle_item,
    update_cycle_item,
    delete_cycle_item
)
from app.services.document.report_services import (get_reports_by_item,get_reports_by_item_paginated)

report_cycle_routes = Blueprint('report_cycle', __name__)

@report_cycle_routes.route('/', methods=['GET'])
@jwt_required
def list_cycles():
    try:
        page   = request.args.get('page',   type=int)
        limit  = request.args.get('limit',  type=int)
        search = request.args.get('search', type=str)
        active = request.args.get('active', type=bool, default=False)

        result = get_cycles_paginated(
            page   or 1,
            limit  or 10,
            search,
            active
        )
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.exception("Error al listar ciclos")
        return jsonify({"error": str(e)}), 500

@report_cycle_routes.route('/<int:cycle_id>', methods=['GET'])
@jwt_required
def get_cycle(cycle_id):
    cycle = get_cycle_by_id(cycle_id)
    if not cycle:
        return jsonify({"message": "Ciclo no encontrado"}), 404
    return jsonify(format_cycle(cycle)), 200

@report_cycle_routes.route('/', methods=['POST'])
@jwt_required
def post_cycle():
    body = request.get_json() or {}
    required = ['name','folder_name','start_date','end_date']
    missing = [k for k in required if not body.get(k)]
    if missing:
        return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400
    try:
        sd = date.fromisoformat(body['start_date'])
        ed = date.fromisoformat(body['end_date'])
        cycle = create_cycle(
            name=body['name'],
            folder_name=body['folder_name'],
            start_date=sd,
            end_date=ed
        )
        return jsonify({
            "message": "Ciclo creado",
            "data": format_cycle(cycle)
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error al crear ciclo")
        return jsonify({"error": str(e)}), 500

@report_cycle_routes.route('/<int:cycle_id>', methods=['PUT'])
@jwt_required
def put_cycle(cycle_id):
    body = request.get_json() or {}
    try:
        sd = date.fromisoformat(body['start_date']) if body.get('start_date') else None
        ed = date.fromisoformat(body['end_date'])   if body.get('end_date')   else None
        cycle = update_cycle(
            cycle_id=cycle_id,
            name=body.get('name'),
            folder_name=body.get('folder_name'),
            start_date=sd,
            end_date=ed
        )
        if not cycle:
            return jsonify({"message": "Ciclo no encontrado"}), 404
        return jsonify({"message": "Ciclo actualizado", "data": format_cycle(cycle)}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error al actualizar ciclo")
        return jsonify({"error": str(e)}), 500

@report_cycle_routes.route('/<int:cycle_id>', methods=['DELETE'])
@jwt_required
def delete_cycle_route(cycle_id):
    try:
        ok = delete_cycle(cycle_id)
        if not ok:
            return jsonify({"message": "Ciclo no encontrado"}), 404
        return jsonify({"message": "Ciclo eliminado"}), 200
    except Exception as e:
        current_app.logger.exception("Error al eliminar ciclo")
        return jsonify({"error": str(e)}), 500

# -- Ítems -- #

@report_cycle_routes.route('/<int:cycle_id>/items', methods=['GET'])
@jwt_required
def list_items(cycle_id):
    try:
        page   = request.args.get('page',  type=int)
        limit  = request.args.get('limit', type=int)
        active = request.args.get('active',type=bool, default=False)

        result = get_cycle_items_paginated(
            cycle_id,
            page  or 1,
            limit or 10,
            active
        )
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.exception("Error al listar ítems")
        return jsonify({"error": str(e)}), 500

@report_cycle_routes.route('/<int:cycle_id>/items/<int:item_id>', methods=['GET'])
@jwt_required
def get_item(cycle_id, item_id):
    item = get_cycle_item_by_id(cycle_id, item_id)
    if not item:
        return jsonify({"message": "Ítem no encontrado"}), 404
    return jsonify(format_cycle_item(item)), 200

@report_cycle_routes.route('/<int:cycle_id>/items', methods=['POST'])
@jwt_required
def post_item(cycle_id):
    body = request.get_json() or {}
    required = ['report_number','title','start_date','end_date']
    missing = [k for k in required if not body.get(k)]
    if missing:
        return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400
    try:
        sd = date.fromisoformat(body['start_date'])
        ed = date.fromisoformat(body['end_date'])
        item = create_cycle_item(
            cycle_id=cycle_id,
            report_number=body['report_number'],
            title=body['title'],
            start_date=sd,
            end_date=ed
        )
        return jsonify({"message": "Ítem creado", "data": format_cycle_item(item)}), 201
    except KeyError as ke:
        return jsonify({"error": str(ke)}), 404
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error al crear ítem")
        return jsonify({"error": str(e)}), 500

@report_cycle_routes.route('/<int:cycle_id>/items/<int:item_id>', methods=['PUT'])
@jwt_required
def put_item(cycle_id, item_id):
    body = request.get_json() or {}
    try:
        sd = date.fromisoformat(body['start_date']) if body.get('start_date') else None
        ed = date.fromisoformat(body['end_date'])   if body.get('end_date')   else None
        item = update_cycle_item(
            cycle_id=cycle_id,
            item_id=item_id,
            report_number=body.get('report_number'),
            title=body.get('title'),
            start_date=sd,
            end_date=ed
        )
        if not item:
            return jsonify({"message": "Ítem no encontrado"}), 404
        return jsonify({"message": "Ítem actualizado", "data": format_cycle_item(item)}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        current_app.logger.exception("Error al actualizar ítem")
        return jsonify({"error": str(e)}), 500

@report_cycle_routes.route('/<int:cycle_id>/items/<int:item_id>', methods=['DELETE'])
@jwt_required
def delete_item(cycle_id, item_id):
    try:
        ok = delete_cycle_item(cycle_id, item_id)
        if not ok:
            return jsonify({"message": "Ítem no encontrado"}), 404
        return jsonify({"message": "Ítem eliminado"}), 200
    except Exception as e:
        current_app.logger.exception("Error al eliminar ítem")
        return jsonify({"error": str(e)}), 500

@report_cycle_routes.route(
    '/<int:cycle_id>/items/<int:item_id>/reports',
    methods=['GET']
)
@jwt_required
def list_reports_for_item(cycle_id, item_id):
    # 1) Validar que el ítem existe y pertenece al ciclo
    item = get_cycle_item_by_id(cycle_id, item_id)
    if not item:
        return jsonify({"message": "Ítem no encontrado"}), 404

    # 2) Leer parámetros de paginación y búsqueda
    page   = request.args.get('page',   type=int) or 1
    limit  = request.args.get('limit',  type=int) or 10
    search = request.args.get('search', type=str)

    # 3) Llamar al servicio
    try:
        result = get_reports_by_item_paginated(
            item_id=item_id,
            page=page,
            limit=limit,
            search=search
        )
    except Exception:
        current_app.logger.exception("Error al listar reportes paginados")
        return jsonify({"error": "Error interno al cargar reportes"}), 500

    # 4) Devolver resultado
    return jsonify(result), 200