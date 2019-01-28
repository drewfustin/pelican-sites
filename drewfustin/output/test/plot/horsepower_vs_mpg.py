import altair as alt

def generate_plot(data_file):
    return (
        alt.Chart(data_file)
        .mark_point()
        .encode(
            x='Horsepower:Q',
            y='Miles_per_Gallon:Q',
            color='Origin:N'
        )
        .interactive()
        .to_json()
    )
