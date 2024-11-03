
from db import db
from models.user import BaseData, Company
import plotly.io as pio
import matplotlib.pyplot as plt
import io
import base64
import plotly.graph_objects as go
from io import BytesIO



class ChartService:

    @staticmethod
    def query_data(company_id=None, area_id=None, subarea_id=None):
        try:
            query = BaseData.query
            if company_id:
                query = query.filter_by(company_id=company_id)
            if area_id:
                query = query.filter_by(area_id=area_id)
            if subarea_id:
                query = query.filter_by(subarea_id=subarea_id)
            return query.all()
        except Exception as e:
            raise ValueError(f"Error querying data: {e}")

    @staticmethod
    def generate_bar_chart(data):
        try:
            fields = [f"fi{i}" for i in range(1, 17)] + [f"fn{i}" for i in range(1, 9)]
            labels = [f"{str(getattr(d, 'fi0'))}/{str(getattr(d, 'interval_id'))}" for d in data]
            values = {field: [getattr(d, field) or 0 for d in data if getattr(d, field) is not None] for field in fields}

            fig, ax = plt.subplots()
            for field, val in values.items():
                if val:
                    ax.bar(labels, val, label=field)

            ax.set_xlabel('Year/Interval')
            ax.set_ylabel('Values')
            ax.set_title('Bar Chart')
            ax.legend()

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

            return image_base64
        except Exception as e:
            raise ValueError(f"Error generating bar chart: {e}")

    @staticmethod
    def generate_3d_chart(data):
        try:
            print("Data for 3D Chart:", data)

            x_values = [f"{str(getattr(d, 'fi0'))}/{str(getattr(d, 'interval_id'))}" for d in data]
            y_values = [d.company.name if d.company else "Unknown" for d in data]

            fields = [f"fi{i}" for i in range(1, 17)] + [f"fn{i}" for i in range(1, 9)]
            z_values = []
            for d in data:
                for field in fields:
                    value = getattr(d, field, None)
                    if value is not None:
                        z_values.append(value)

            print("x_values:", x_values)
            print("y_values:", y_values)
            print("z_values:", z_values)

            if not x_values or not y_values or not z_values:
                raise ValueError("One of the axis values is empty. Ensure data is correctly passed.")

            trace = go.Scatter3d(
                x=x_values,
                y=y_values,
                z=z_values,
                mode='markers',
                marker=dict(size=5, color=z_values, colorscale='Viridis')
            )

            layout = go.Layout(
                title='3D Bar Chart',
                scene=dict(
                    xaxis=dict(title='Year/Interval'),
                    yaxis=dict(title='Company Name'),
                    zaxis=dict(title='Values')
                ),
                autosize=True,
                margin=dict(l=0, r=0, b=0, t=40),
                height=800,
                width=1200
            )

            fig = go.Figure(data=[trace], layout=layout)
            chart_html = pio.to_html(fig, full_html=False)

            return chart_html
        except Exception as e:
            raise ValueError(f"Error generating 3D chart: {e}")

    @staticmethod
    def get_non_null_fields(data):
        if not data:
            return []
        first_row = data[0]
        return [column for column in first_row.__table__.columns.keys() if getattr(first_row, column) is not None]
