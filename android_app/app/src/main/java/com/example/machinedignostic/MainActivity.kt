package com.example.machinedignostic

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.filled.UploadFile
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.DataOutputStream
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme(
                colorScheme = darkColorScheme(
                    primary = Color(0xFF6200EE),
                    secondary = Color(0xFFFF4081),
                    background = Color(0xFF10101C)
                )
            ) {
                Surface(modifier = Modifier.fillMaxSize()) {
                    MachineDiagnosticUI()
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MachineDiagnosticUI() {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    
    // States
    // Typo in original default URL fixed here
    var serverUrl by remember { mutableStateOf("https://rudragamerz-mechanic-fault-detector.hf.space") }
    var resultText by remember { mutableStateOf("Ready") }
    var confidenceText by remember { mutableStateOf("") }
    var isRecording by remember { mutableStateOf(false) }

    // Helpers for UI Logic
    val isNormal = resultText.lowercase(Locale.ROOT).contains("normal")
    val isAbnormal = resultText.lowercase(Locale.ROOT).contains("abnormal") || 
                     resultText.lowercase(Locale.ROOT).contains("fault")
    
    // Dynamic Colors
    val resultColor by animateColorAsState(
        targetValue = when {
            isNormal -> Color(0xFF00E676) // Bright Green
            isAbnormal -> Color(0xFFFF5252) // Red
            else -> Color(0xFF6200EE) // Default Purple/Neutral
        }, label = "color"
    )

    val resultIcon: ImageVector? = when {
        isNormal -> Icons.Default.CheckCircle
        isAbnormal -> Icons.Default.Warning
        else -> null
    }

    // Permission Launcher
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        if (permissions[Manifest.permission.RECORD_AUDIO] == false) {
            Toast.makeText(context, "Permission Denied", Toast.LENGTH_SHORT).show()
        }
    }

    // File Picker
    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            val file = uriToFile(context, it)
            if (file != null) {
                resultText = "Uploading..."
                confidenceText = ""
                scope.launch {
                    uploadAudio(file, serverUrl) { res ->
                        val (p, c) = parseResultWithError(res)
                        resultText = p
                        confidenceText = c
                    }
                }
            } else {
                Toast.makeText(context, "File Error", Toast.LENGTH_SHORT).show()
            }
        }
    }

    // Main Layout
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(Color(0xFF1A1A2E), Color(0xFF000000))
                )
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(20.dp))

            // Logo with Glow effect (Simulated by border)
            Box(
                modifier = Modifier
                    .size(160.dp)
                    .clip(CircleShape)
                    .background(Color.Black)
                    .border(3.dp, resultColor, CircleShape), // Border changes with result
                contentAlignment = Alignment.Center
            ) {
                Image(
                    painter = painterResource(id = R.drawable.app_logo),
                    contentDescription = "Logo",
                    modifier = Modifier.fillMaxSize()
                )
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Result Card
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(150.dp),
                shape = RoundedCornerShape(24.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF16213E).copy(alpha = 0.8f) // Translucent Dark Blue
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
            ) {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    if (resultIcon != null) {
                        Icon(
                            imageVector = resultIcon,
                            contentDescription = null,
                            tint = resultColor,
                            modifier = Modifier.size(32.dp)
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                    }
                    
                    Text(
                        text = resultText,
                        fontSize = 26.sp,
                        fontWeight = FontWeight.Bold,
                        color = resultColor
                    )
                    
                    // Confidence text removed as per user request
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // URL Input Hidden as per user request
            // Maintained layout with Spacer below
            Spacer(modifier = Modifier.height(10.dp))

            Spacer(modifier = Modifier.weight(1f))

            // Action Buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Upload Button
                Button(
                    onClick = { filePickerLauncher.launch("audio/*") },
                    modifier = Modifier
                        .weight(1f)
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF3F51B5)), // Indigo
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Icon(Icons.Default.UploadFile, contentDescription = null, tint = Color.White)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("UPLOAD", fontWeight = FontWeight.Bold, color = Color.White)
                }

                // Record Button
                Button(
                    onClick = {
                        if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                            if (!isRecording) {
                                isRecording = true
                                resultText = "Listening..."
                                confidenceText = ""
                                val file = File(context.cacheDir, "recording.wav")
                                val recorder = AudioPreprocessor()
                                recorder.startRecording(file)

                                scope.launch {
                                    kotlinx.coroutines.delay(5000)
                                    recorder.stopRecording()
                                    isRecording = false
                                    resultText = "Analyzing..."
                                    uploadAudio(file, serverUrl) { res ->
                                        val (p, c) = parseResultWithError(res)
                                        resultText = p
                                        confidenceText = c
                                    }
                                }
                            }
                        } else {
                            permissionLauncher.launch(arrayOf(Manifest.permission.RECORD_AUDIO))
                        }
                    },
                    modifier = Modifier
                        .weight(1f)
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (isRecording) Color(0xFFFF5252) else Color(0xFFFF4081)
                    ),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Icon(Icons.Default.Mic, contentDescription = null, tint = Color.White)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(if (isRecording) "STOP" else "RECORD", fontWeight = FontWeight.Bold, color = Color.White)
                }
            }
            Spacer(modifier = Modifier.height(20.dp))
        }
    }
}

// --- Logic Improvement ---

fun parseResultWithError(jsonString: String): Pair<String, String> {
    return try {
        if (jsonString.trim().startsWith("<")) {
            return Pair("Server Error", "Check URL")
        }
        val json = JSONObject(jsonString)
        
        // Robust Key Checking: Check multiple common keys for the prediction result
        val keysToCheck = listOf("prediction", "label", "class", "result", "status")
        var result = "Unknown"
        
        for (key in keysToCheck) {
            if (json.has(key)) {
                result = json.getString(key)
                break
            }
        }
        
        // Capitalize result for display
        result = result.replaceFirstChar { if (it.isLowerCase()) it.titlecase(Locale.getDefault()) else it.toString() }

        val confVal = if (json.has("confidence")) json.get("confidence") else null
        val conf = when (confVal) {
            is Double -> "${"%.1f".format(confVal * 100)}%" // Assuming server sends 0-1, scaling to %
            is String -> confVal // If server already sends string like "99%"
            else -> ""
        }
        
        // If still unknown but we have whole JSON, maybe show keys? 
        // For now, "Unknown" is better than crashing, but the loop above works for 99% of servers.
        
        Pair(result, conf)
    } catch (e: Exception) {
        Pair("Parse Error", "")
    }
}

fun uriToFile(context: Context, uri: Uri): File? {
    return try {
        val inputStream = context.contentResolver.openInputStream(uri)
        val file = File(context.cacheDir, "temp_upload.wav")
        val outputStream = FileOutputStream(file)
        inputStream?.copyTo(outputStream)
        inputStream?.close()
        outputStream.close()
        file
    } catch (e: Exception) { null }
}

suspend fun uploadAudio(file: File, serverUrl: String, onResult: (String) -> Unit) {
    withContext(Dispatchers.IO) {
        try {
            // Ensure no double slash if user adds one
            val baseUrl = serverUrl.trimEnd('/')
            val endpoint = "$baseUrl/predict"
            
            val url = URL(endpoint)
            val conn = url.openConnection() as HttpURLConnection
            val boundary = "---ContentBoundary"
            
            conn.requestMethod = "POST"
            conn.doOutput = true
            conn.doInput = true
            conn.useCaches = false
            conn.setRequestProperty("Content-Type", "multipart/form-data; boundary=$boundary")
            conn.connectTimeout = 5000 // 5s timeout
            conn.readTimeout = 10000 // 10s read timeout

            val out = DataOutputStream(conn.outputStream)
            val lineEnd = "\r\n"
            
            out.writeBytes("--$boundary$lineEnd")
            out.writeBytes("Content-Disposition: form-data; name=\"file\"; filename=\"${file.name}\"$lineEnd")
            out.writeBytes(lineEnd)
            
            val fis = FileInputStream(file)
            val buffer = ByteArray(4096)
            var bytesRead: Int
            while (fis.read(buffer).also { bytesRead = it } != -1) {
                out.write(buffer, 0, bytesRead)
            }
            fis.close()
            
            out.writeBytes(lineEnd)
            out.writeBytes("--$boundary--$lineEnd")
            out.flush()
            out.close()

            val responseCode = conn.responseCode
            if (responseCode == 200) {
                val response = conn.inputStream.bufferedReader().use { it.readText() }
                withContext(Dispatchers.Main) { onResult(response) }
            } else {
                withContext(Dispatchers.Main) { onResult("Error: $responseCode") }
            }
        } catch (e: java.net.SocketTimeoutException) {
             withContext(Dispatchers.Main) { onResult("Timeout") }
        } catch (e: Exception) {
            e.printStackTrace()
            withContext(Dispatchers.Main) { onResult("Conn Failed") }
        }
    }
}
