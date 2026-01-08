package com.example.machinedignostic

import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import org.json.JSONObject
import java.io.BufferedReader
import java.io.File
import java.io.FileInputStream
import java.io.InputStreamReader
import java.io.OutputStream
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : AppCompatActivity() {

    private val preprocessor = AudioPreprocessor()
    
    private lateinit var statusText: TextView
    private lateinit var confidenceText: TextView
    private lateinit var recordButton: Button
    
    // Default IP, user can change this via Dialog
    private var serverIp = "192.168.1.10" 

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        statusText = findViewById(R.id.statusText)
        confidenceText = findViewById(R.id.confidenceText)
        recordButton = findViewById(R.id.recordButton)

        // Show IP dialog on start or long press of record button
        showIpDialog()

        recordButton.setOnLongClickListener {
            showIpDialog()
            true
        }

        recordButton.setOnClickListener {
            if (checkPermission()) {
                startDiagnostic()
            } else {
                requestPermission()
            }
        }
    }

    private fun showIpDialog() {
        val builder = AlertDialog.Builder(this)
        builder.setTitle("Enter server IP or URL")
        builder.setMessage("Enter Local IP (e.g. 192.168.1.5) OR Public URL (e.g. https://...ngrok.io)")
        
        val input = EditText(this)
        input.hint = "IP or URL"
        input.setText(serverIp)
        builder.setView(input)

        builder.setPositiveButton("OK") { dialog, _ ->
            serverIp = input.text.toString().trim()
            Toast.makeText(this, "Server Address set to $serverIp", Toast.LENGTH_SHORT).show()
        }
        builder.setNegativeButton("Cancel") { dialog, _ -> dialog.cancel() }

        builder.show()
    }

    private fun startDiagnostic() {
        statusText.text = "Recording & Sending..."
        recordButton.isEnabled = false
        
        Thread {
            try {
                // 1. Record to WAV
                val audioFile = File(cacheDir, "audio_capture.wav")
                val success = preprocessor.recordToWav(audioFile)
                
                if (success) {
                    // 2. Upload to Server
                    runOnUiThread { statusText.text = "Uploading..." }
                    
                    // Determine full URL
                    val fullUrl = if (serverIp.startsWith("http")) {
                        if (serverIp.endsWith("/")) "${serverIp}predict" else "$serverIp/predict"
                    } else {
                        "http://$serverIp:5000/predict"
                    }
                    
                    val responseParams = uploadFile(audioFile, fullUrl)
                    
                    if (responseParams != null) {
                        val score = responseParams.getDouble("score").toFloat()
                        val label = responseParams.getString("label")
                        val confidence = responseParams.getDouble("confidence").toInt()
                         
                        runOnUiThread { updateUI(label, confidence, score) }
                    } else {
                         runOnUiThread { statusText.text = "Fail: Server Unreachable" }
                    }
                } else {
                     runOnUiThread { statusText.text = "Mic/File Error" }
                }
            } catch (e: Exception) {
                e.printStackTrace()
                runOnUiThread { statusText.text = "Error: ${e.message}" }
            } finally {
                runOnUiThread { recordButton.isEnabled = true }
            }
        }.start()
    }

    private fun uploadFile(file: File, serverUrl: String): JSONObject? {
        val boundary = "*****" + System.currentTimeMillis() + "*****"
        val lineEnd = "\r\n"
        val twoHyphens = "--"

        try {
            val url = URL(serverUrl)
            val connection = url.openConnection() as HttpURLConnection
            connection.doInput = true
            connection.doOutput = true
            connection.useCaches = false
            connection.requestMethod = "POST"
            connection.setRequestProperty("Connection", "Keep-Alive")
            connection.setRequestProperty("Content-Type", "multipart/form-data; boundary=$boundary")
            // Bypass Ngrok Warning Page
            connection.setRequestProperty("ngrok-skip-browser-warning", "true")
            connection.setRequestProperty("User-Agent", "MachineDiagnosticApp")
            
            // Helpful timeout settings
            connection.connectTimeout = 10000 
            connection.readTimeout = 10000

            val outputStream: OutputStream = connection.outputStream
            val writer = java.io.PrintWriter(java.io.OutputStreamWriter(outputStream, "UTF-8"), true)

            // Write File Header
            writer.append(twoHyphens + boundary + lineEnd)
            writer.append("Content-Disposition: form-data; name=\"file\"; filename=\"" + file.name + "\"" + lineEnd)
            writer.append("Content-Type: audio/wav" + lineEnd)
            writer.append(lineEnd)
            writer.flush()

            // Write File Data
            val fileInputStream = FileInputStream(file)
            val buffer = ByteArray(4096)
            var bytesRead: Int
            while (fileInputStream.read(buffer).also { bytesRead = it } != -1) {
                outputStream.write(buffer, 0, bytesRead)
            }
            outputStream.flush()
            fileInputStream.close()

            // End of multipart
            writer.append(lineEnd)
            writer.flush()
            writer.append(twoHyphens + boundary + twoHyphens + lineEnd)
            writer.close()

            // Get Response
            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val reader = BufferedReader(InputStreamReader(connection.inputStream))
                val sb = StringBuilder()
                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    sb.append(line)
                }
                reader.close()
                return JSONObject(sb.toString())
            } else {
                return null
            }
        } catch (e: Exception) {
            e.printStackTrace()
            return null
        }
    }

    private fun updateUI(label: String, confidence: Int, score: Float) {
        val color: Int
        
        if (score > 0.5f) { // Fault
            color = ContextCompat.getColor(this, android.R.color.holo_red_dark)
        } else { // Normal
            color = ContextCompat.getColor(this, android.R.color.holo_green_dark)
        }
        
        statusText.text = label
        statusText.setTextColor(color)
        confidenceText.text = "Confidence: $confidence%"
    }

    private fun checkPermission(): Boolean {
        return ContextCompat.checkSelfPermission(this, android.Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED
    }

    private fun requestPermission() {
        ActivityCompat.requestPermissions(this, arrayOf(android.Manifest.permission.RECORD_AUDIO), 100)
    }
}
