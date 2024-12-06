from __init__ import CURSOR, CONN
from employee import Employee

class Review:
    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year  # Validation happens here
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee ID: {self.employee_id}>"
        )

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        if isinstance(year, int) and year >= 2000:
            self._year = year
        else:
            raise ValueError("Year must be an integer and greater than or equal to 2000")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        if isinstance(summary, str) and summary.strip():
            self._summary = summary.strip()
        else:
            raise ValueError("Summary must be a non-empty string")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id):
        if isinstance(employee_id, int) and Employee.find_by_id(employee_id):
            self._employee_id = employee_id
        else:
            raise ValueError("Employee ID must reference a valid employee")

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Review instances."""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INT,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Review instances."""
        sql = "DROP TABLE IF EXISTS reviews;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert or update a row with the current Review instance's attributes."""
        if self.id is None:
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid  # Assign the ID of the newly inserted row
            Review.all[self.id] = self  # Save the object in the dictionary
        else:
            self.update()
        CONN.commit()

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE reviews SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance."""
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        if self.id in Review.all:
            del Review.all[self.id]
        self.id = None  # Reset ID to None
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """Initialize a new Review instance and save it to the database."""
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance from a database row."""
        if not row:
            return None
        review = cls.all.get(row[0])
        if review:
            # Update existing instance attributes
            review.year, review.summary, review.employee_id = row[1:4]
        else:
            # Create a new instance and add it to the dictionary
            review = cls(row[1], row[2], row[3], id=row[0])
            cls.all[row[0]] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        """Find a Review instance by its ID."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row)

    @classmethod
    def get_all(cls):
        """Return a list of all Review instances."""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_employee_id(cls, employee_id):
        """Find all reviews associated with a specific employee."""
        sql = "SELECT * FROM reviews WHERE employee_id = ?"
        rows = CURSOR.execute(sql, (employee_id,)).fetchall()
        return [cls.instance_from_db(row) for row in rows]
