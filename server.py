import os
from aiohttp import request
from flask import Flask, jsonify, send_from_directory, render_template, redirect
import json
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
import pandas as pd

app = Flask(__name__)

port = int(os.environ.get("PORT", 5000))

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/<path:path>')
def all_routes(path):
    return redirect('/')

os.environ["OPENAI_API_KEY"] = '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'

@app.route('/evaluate', methods=['GET'])
def evaluate_answers():
    try:
        # data_request = request.json

        # questions = data_request.get("questions", [])
        # ground_truth = data_request.get("ground_truth", [])
        # answers = data_request.get("answers", [])
        # contexts = data_request.get("contexts", [])
        print('uno')
        questions = [
                    "Qué dijo el presidente sobre la crisis política?", 
                    ]
        # Después
        ground_truth = [
        "El presidente dijo que la crisis política se debe a la corrupción y la inflación",
        ]

        answers = [
            ["El presidente dijo que la crisis política es a causa de la corrupción"],
        ]
        # answers = []
        # contexts = []
        contexts = [
            ["El presidente mencionó en su discurso que la crisis política que atravesamos se debe al crecimiento de la corrupción",]
        ]

        data = {
            "question": questions,
            "answer": [str(answer) for answer in answers],  # Convertir todos los valores a cadenas
            "contexts": contexts,
            "ground_truth": ground_truth
        }
        dataset = Dataset.from_dict(data)
        print('dos')
        result = evaluate(
            dataset=dataset, 
            metrics=[
                context_precision,
                context_recall,
                faithfulness,
                answer_relevancy,
            ],
            raise_exceptions=False
        )
        print('tres')
        pd.set_option("display.max_colwidth", None)
        df = result.to_pandas()

        # Convertir el DataFrame a un diccionario
        result_dict = df.to_dict(orient="records")

        # Convertir cualquier ndarray a lista para que sea JSON serializable
        result_dict_serializable = json.loads(json.dumps(result_dict, default=lambda x: x.tolist()))

        return jsonify({
            "statusCode": 200,
            "body": result_dict_serializable,
        })

    except Exception as e:
        return jsonify({
            "statusCode": 500,
            "body": f"Error during evaluation: {str(e)}",
        })

if __name__ == "__main__":
    app.run(port=port)