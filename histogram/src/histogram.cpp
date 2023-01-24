#include<iostream>
#include<vector>
#include<algorithm>
#include<fstream>

using std::vector;
using std::pair;

using std::cout;
using std::endl;
using std::ifstream;

const int CHAR_CNT = 26;

bool is_valid(char c) {
  return ('a' <= c && c <= 'z');
}

vector<pair<char,int>> build_histogram(){
  vector<pair<char,int>> histogram(CHAR_CNT);
  for(int i = 0; i < CHAR_CNT; i++)
    histogram[i].first = 'a' + i;
  return histogram;
}

vector<pair<char,int>> read_file(ifstream &file) {
  auto histogram = build_histogram();

  try {
    char c;
    while(file >> c) {
      c = tolower(c);
      if(is_valid(c)) histogram[c - 'a'].second++;
    }
  } catch (const ifstream::failure& e) {
    cout << "Failure while reading file. Returning partial histogram..." << endl;
  }

  return histogram;
}

void print(char* filename, const vector<pair<char,int>> &histogram) {
  cout << filename << "\n";
  for(auto [carac, count] : histogram) {
    if(count == 0) break;
    cout << carac << " " << count << "\n";
  }
  cout << endl;
}

int main(int argc, char **argv) {
  for(int i = 1; i < argc; ++i) {
    char* filename = argv[i];
    ifstream file(filename);
    file.exceptions(ifstream::badbit);
    
    auto histogram = read_file(file);

    sort(histogram.begin(), histogram.end(), [](pair<char,int> x, pair<char,int> y){
      if(x.second == y.second) return x.first < y.first;
      else return x.second > y.second;
    });

    print(filename, histogram);
  }
}