import boto3
from yattag import Doc, indent

client = boto3.client('textract')
doc, tag, text = Doc().tagtext()

def resultsParser(result):
    result_data = {}

    for line in result["Blocks"][0]["Relationships"][0]["Ids"]:
        result_data[line] = {}

    for line in result_data:
        for block in result["Blocks"]:
            if block["Id"] == line:
                result_data[line] = {
                    "BlockType": block["BlockType"],
                    "Confidence": block["Confidence"],
                    "Text": block["Text"],
                    "BoundingBox": {
                        "Width": block["Geometry"]["BoundingBox"]["Width"],
                        "Height": block["Geometry"]["BoundingBox"]["Height"],
                        "Left": block["Geometry"]["BoundingBox"]["Left"],
                        "Top": block["Geometry"]["BoundingBox"]["Top"],
                    },
                    "Polygon": [
                        {
                            "X": block["Geometry"]["Polygon"][0]["X"],
                            "Y": block["Geometry"]["Polygon"][0]["Y"]
                        },
                        {
                            "X": block["Geometry"]["Polygon"][1]["X"],
                            "Y": block["Geometry"]["Polygon"][1]["Y"]
                        },
                        {
                            "X": block["Geometry"]["Polygon"][2]["X"],
                            "Y": block["Geometry"]["Polygon"][2]["Y"]
                        },
                        {
                            "X": block["Geometry"]["Polygon"][3]["X"],
                            "Y": block["Geometry"]["Polygon"][3]["Y"]
                        }
                    ],
                    "Words": {}
                }

                for wordid in block["Relationships"][0]["Ids"]:
                    result_data[line]["Words"][wordid] = {}
                break

    for line in result_data:
        for word in result_data[line]["Words"]:
            for block in result["Blocks"]:
                if block["Id"] == word:
                    result_data[line]["Words"][word] = {
                        "BlockType": block["BlockType"],
                        "Confidence": block["Confidence"],
                        "Text": block["Text"],
                        "TextType": block["TextType"],
                        "BoundingBox": {
                            "Width": block["Geometry"]["BoundingBox"]["Width"],
                            "Height": block["Geometry"]["BoundingBox"]["Height"],
                            "Left": block["Geometry"]["BoundingBox"]["Left"],
                            "Top": block["Geometry"]["BoundingBox"]["Top"],
                        },
                        "Polygon": [
                            {
                                "X": block["Geometry"]["Polygon"][0]["X"],
                                "Y": block["Geometry"]["Polygon"][0]["Y"]
                             },
                            {
                                "X": block["Geometry"]["Polygon"][1]["X"],
                                "Y": block["Geometry"]["Polygon"][1]["Y"]
                            },
                            {
                                "X": block["Geometry"]["Polygon"][2]["X"],
                                "Y": block["Geometry"]["Polygon"][2]["Y"]
                            },
                            {
                                "X": block["Geometry"]["Polygon"][3]["X"],
                                "Y": block["Geometry"]["Polygon"][3]["Y"]
                            }
                        ]
                    }
                    break
    printHTML(result_data)

def printHTML(result_data):
    with tag('html'):
        with tag('body'):
            with tag('div', klass="ocr_page"):
                for line in result_data:
                    with tag('div', ('title', 'bbox '
                                              + str(int(result_data[line]["BoundingBox"]["Width"]*1000))
                                              +' '+ str(int(result_data[line]["BoundingBox"]["Height"]*1000))
                                              +' '+ str(int(result_data[line]["BoundingBox"]["Left"]*1000))
                                              +' '+ str(int(result_data[line]["BoundingBox"]["Top"]*1000))
                                              + '; x_wconf '+ str(int(result_data[line]["Confidence"]))
                                     ), klass='ocr_line'):
                        for word in result_data[line]["Words"]:
                            with tag('span', ('title', 'bbox '
                                                      + str(int(result_data[line]["Words"][word]["BoundingBox"]["Width"]*1000))
                                                      + ' ' + str(int(result_data[line]["Words"][word]["BoundingBox"]["Height"]*1000))
                                                      + ' ' + str(int(result_data[line]["Words"][word]["BoundingBox"]["Left"]*1000))
                                                      + ' ' + str(int(result_data[line]["Words"][word]["BoundingBox"]["Top"]*1000))
                                                       + '; x_wconf ' + str(int(result_data[line]["Words"][word]["Confidence"]))
                                              ), klass='ocrx_word'):
                                text(result_data[line]["Words"][word]["Text"]+' ')

    with open('hocr-output.html', 'w') as f:
        print(indent(doc.getvalue()), file=f)
    print("Results printed out to output.html")

if __name__ == '__main__':
    try:
        response = client.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': 'INSERT-BUCKET-NAME',
                    'Name': 'INSERT-FILE-NAME',
                }
            }
        )
        resultsParser(response)

    except client.exceptions.UnsupportedDocumentException as e:
        print("File not supported, please provide a PNG or JPEG file. For PDF use async jobs.")