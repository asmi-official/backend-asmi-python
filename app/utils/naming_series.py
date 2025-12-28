from sqlalchemy.orm import Session
from app.models.naming_series import NamingSeries


def get_next_code(
    code_prefix: str,
    db: Session,
    padding_length: int = 12,
    description: str | None = None
) -> str:
    """
    Generate kode berikutnya berdasarkan code_prefix dari tabel naming_series.
    Jika code_prefix belum ada, otomatis create baru.

    IMPORTANT: Fungsi ini TIDAK melakukan commit, jadi harus di-commit oleh caller.
    Ini untuk memastikan atomicity dengan operasi lainnya.

    Args:
        code_prefix: Prefix kode (BUS, ORD, INV, PRD, TRX, dll)
        db: Database session
        padding_length: Jumlah digit untuk padding (default: 12)
        description: Deskripsi untuk series (optional)

    Returns:
        String kode dengan format: {PREFIX}{PADDED_NUMBER}
        Contoh: BUS000000000001, TRX000000000001

    Example:
        >>> code = get_next_code("BUS", db, padding_length=12, description="Business code")
        >>> # ... operasi lainnya ...
        >>> db.commit()  # Commit di akhir semua operasi
    """
    # Ambil naming series berdasarkan prefix dengan lock
    naming_series = db.query(NamingSeries).filter(
        NamingSeries.code_prefix == code_prefix
    ).with_for_update().first()

    # Jika belum ada, create baru
    if not naming_series:
        naming_series = NamingSeries(
            code_prefix=code_prefix,
            last_number=0,
            padding_length=padding_length,
            description=description or f"{code_prefix} code series"
        )
        db.add(naming_series)
        db.flush()  # Flush untuk mendapatkan ID dan lock

    # Increment last_number
    naming_series.last_number += 1
    next_number = naming_series.last_number

    # Format dengan padding
    padded_number = str(next_number).zfill(naming_series.padding_length)

    # Generate kode lengkap
    generated_code = f"{naming_series.code_prefix}{padded_number}"

    # TIDAK melakukan commit, biar caller yang handle
    # Ini penting untuk transaction atomicity

    return generated_code


