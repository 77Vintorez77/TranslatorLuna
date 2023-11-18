from translator.basetranslator import basetrans
import sys
import os
import subprocess,os,platform

class TS(basetrans):  

    def translate_sentence(self, sentence):
        input_enc = self.tokenizer.encode('<-ja2zh-> ' + sentence)
        input_ids = input_enc.ids
        int_seq = [len(input_ids)] + input_ids + ['\n']
        pipe_in = " ".join([str(i) for i in int_seq])
        self.proc.stdin.write(pipe_in)
        pipe_out = self.proc.stdout.readline()
        output_ids = [int(i) for i in pipe_out.split()]
        return self.tokenizer.decode(output_ids)
    def end(self):
        self.proc.kill()
    def inittranslator(self):
        self.checkempty(['路径'])
        path=self.config['路径']
        if os.path.exists(path)==False:
            return False
        model_path_candidates = [i for i in os.listdir(os.path.join(path,'model')) if i.endswith(".onnx")]
        if len(model_path_candidates) > 0:
            model_path = os.path.join(path, 'model', model_path_candidates[0])
        else:
            return "mT5 onnx file not found!"
        tok_path                 = os.path.join(path,'model/tokenizer.json')#str(self.config['Tokenizer路径'])
        if platform.architecture()[0]=="64bit":
            ort_mt5_path             = os.path.join(path,'bin/x64/ortmt5.exe')
        else:
            ort_mt5_path             = os.path.join(path,'bin/x86/ortmt5.exe')
        
        max_length_int           = int(self.config['最大生成长度'])
        min_length_int           = int(self.config['最小生成长度'])
        num_beams_int            = int(self.config['柱搜索数'])
        num_return_sequences_int = int(self.config['序列数'])
        length_penalty_float     = float(self.config['过长惩罚'])
        repetition_penalty_float = float(self.config['重复惩罚'])
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow=subprocess.SW_HIDE
        self.proc = subprocess.Popen([ort_mt5_path, model_path, str(max_length_int), str(min_length_int), str(num_beams_int), str(num_return_sequences_int), str(length_penalty_float), str(repetition_penalty_float)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True,startupinfo=startupinfo)

        if platform.architecture()[0]=="64bit":
            sys.path.append(os.path.join(path,'libtokenizers/x64'))
        else:
            sys.path.append(os.path.join(path,'libtokenizers/x86'))
        from tokenizers import Tokenizer
        self.tokenizer = Tokenizer.from_file(tok_path)

    def translate(self, content):
        translated = self.translate_sentence(content)
        return translated
