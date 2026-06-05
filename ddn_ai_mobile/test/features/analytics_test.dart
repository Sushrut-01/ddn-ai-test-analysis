import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:dartz/dartz.dart';

void main() {
  group('AnalyticsRepository', () {
    // late MockAnalyticsApiService mockApiService;
    // late AnalyticsRepositoryImpl repository;

    setUp(() {
      // mockApiService = MockAnalyticsApiService();
      // repository = AnalyticsRepositoryImpl(
      //   apiService: mockApiService,
      //   networkInfo: mockNetworkInfo,
      //   hiveManager: mockHiveManager,
      // );
    });

    group('getDashboardData', () {
      test('should return AnalyticsEntity when call is successful', () async {
        // const testBuildId = 'build-123';
        // 
        // when(mockApiService.getDashboardData(testBuildId)).thenAnswer(
        //   (_) async => AnalyticsDataModel(
        //     buildId: testBuildId,
        //     totalFailures: 42,
        //     criticalCount: 5,
        //     highCount: 10,
        //     mediumCount: 15,
        //     lowCount: 12,
        //     successRate: 95.5,
        //     avgResolutionTime: 120,
        //     topFailures: [],
        //   ),
        // );
        //
        // final result = await repository.getDashboardData(testBuildId);
        //
        // expect(result, isA<Right>());
        // verify(mockApiService.getDashboardData(testBuildId)).called(1);
      });
    });

    group('getTrendData', () {
      test('should return list of TrendEntity', () async {
        // TODO: Implement test
      });
    });
  });
}
