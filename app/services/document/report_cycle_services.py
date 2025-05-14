from datetime import datetime, date
from math import ceil
from sqlalchemy import or_
from app.extensions import db
from app.models.document.report_cycle import ReportCycle
from app.models.document.report_cycle_item import ReportCycleItem


def format_cycle(cycle: ReportCycle) -> dict:
    return {
        "cycle_id":    cycle.cycle_id,
        "name":        cycle.name,
        "folder_name": cycle.folder_name,
        "start_date":  cycle.start_date.isoformat(),
        "end_date":    cycle.end_date.isoformat(),
        "created_at":  cycle.created_at.isoformat(),
        "updated_at":  cycle.updated_at.isoformat() if cycle.updated_at else None
    }


def format_cycle_item(item: ReportCycleItem) -> dict:
    return {
        "item_id":      item.item_id,
        "cycle_id":     item.cycle_id,
        "report_number": item.report_number,
        "title":         item.title,
        "start_date":    item.start_date.isoformat(),
        "end_date":      item.end_date.isoformat(),
    }


def get_cycles_paginated(
    page: int = 1,
    limit: int = 10,
    search: str = None,
    active_only: bool = False
) -> dict:
    query = ReportCycle.query

    if search:
        pat = f"%{search}%"
        query = query.filter(
            or_(
                ReportCycle.name.ilike(pat),
                ReportCycle.folder_name.ilike(pat)
            )
        )
    if active_only:
        today = date.today()
        query = query.filter(
            ReportCycle.start_date <= today,
            ReportCycle.end_date >= today
        )

    total = query.count()
    recs = (
        query.order_by(ReportCycle.start_date.desc())
             .offset((page - 1) * limit)
             .limit(limit)
             .all()
    )
    items = [format_cycle(c) for c in recs]
    pages = ceil(total / limit) if total else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }


def get_cycle_by_id(cycle_id: int) -> ReportCycle | None:
    return ReportCycle.query.filter_by(cycle_id=cycle_id).first()


def create_cycle(
    name: str,
    folder_name: str,
    start_date: date,
    end_date: date
) -> ReportCycle:
    if start_date > end_date:
        raise ValueError("La fecha de inicio debe ser anterior a la de fin")
    cycle = ReportCycle(
        name=name,
        folder_name=folder_name,
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(cycle)
    db.session.commit()
    return cycle


def update_cycle(
    cycle_id: int,
    name: str = None,
    folder_name: str = None,
    start_date: date = None,
    end_date: date = None
) -> ReportCycle | None:
    cycle = ReportCycle.query.get(cycle_id)
    if not cycle:
        return None
    if start_date and end_date and start_date > end_date:
        raise ValueError("La fecha de inicio debe ser anterior a la de fin")
    if name:
        cycle.name = name
    if folder_name:
        cycle.folder_name = folder_name
    if start_date:
        cycle.start_date = start_date
    if end_date:
        cycle.end_date = end_date
    cycle.updated_at = datetime.utcnow()
    db.session.commit()
    return cycle


def delete_cycle(cycle_id: int) -> bool:
    cycle = ReportCycle.query.get(cycle_id)
    if not cycle:
        return False
    db.session.delete(cycle)
    db.session.commit()
    return True

# -- Ítems de ciclo -- #

def get_cycle_items_paginated(
    cycle_id: int,
    page: int = 1,
    limit: int = 10,
    active_only: bool = False
) -> dict:
    query = ReportCycleItem.query.filter_by(cycle_id=cycle_id)
    if active_only:
        today = date.today()
        query = query.filter(
            ReportCycleItem.start_date <= today,
            ReportCycleItem.end_date >= today
        )

    total = query.count()
    recs = (
        query.order_by(ReportCycleItem.report_number)
             .offset((page - 1) * limit)
             .limit(limit)
             .all()
    )
    items = [format_cycle_item(i) for i in recs]
    pages = ceil(total / limit) if total else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }


def get_cycle_item_by_id(
    cycle_id: int,
    item_id: int
) -> ReportCycleItem | None:
    return ReportCycleItem.query.filter_by(
        cycle_id=cycle_id,
        item_id=item_id
    ).first()


def create_cycle_item(
    cycle_id: int,
    report_number: int,
    title: str,
    start_date: date,
    end_date: date
) -> ReportCycleItem:
    if start_date > end_date:
        raise ValueError("La fecha de inicio debe ser anterior a la de fin")
    cycle = ReportCycle.query.get(cycle_id)
    if not cycle:
        raise KeyError(f"No existe el ciclo {cycle_id}")
    # Evitar duplicados en report_number
    existing = ReportCycleItem.query.filter_by(
        cycle_id=cycle_id,
        report_number=report_number
    ).first()
    if existing:
        raise ValueError(f"Ya existe un ítem #{report_number} en el ciclo {cycle_id}")

    item = ReportCycleItem(
        cycle_id=cycle_id,
        report_number=report_number,
        title=title,
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(item)
    db.session.commit()
    return item


def update_cycle_item(
    cycle_id: int,
    item_id: int,
    report_number: int = None,
    title: str = None,
    start_date: date = None,
    end_date: date = None
) -> ReportCycleItem | None:
    item = ReportCycleItem.query.filter_by(
        cycle_id=cycle_id,
        item_id=item_id
    ).first()
    if not item:
        return None
    if start_date and end_date and start_date > end_date:
        raise ValueError("La fecha de inicio debe ser anterior a la de fin")
    if report_number:
        dup = ReportCycleItem.query.filter_by(
            cycle_id=cycle_id,
            report_number=report_number
        ).first()
        if dup and dup.item_id != item_id:
            raise ValueError(
                f"Otro ítem con número {report_number} ya existe"
            )
        item.report_number = report_number
    if title:
        item.title = title
    if start_date:
        item.start_date = start_date
    if end_date:
        item.end_date = end_date
    db.session.commit()
    return item


def delete_cycle_item(
    cycle_id: int,
    item_id: int
) -> bool:
    item = ReportCycleItem.query.filter_by(
        cycle_id=cycle_id,
        item_id=item_id
    ).first()
    if not item:
        return False
    db.session.delete(item)
    db.session.commit()
    return True